import threading
import hashlib
import json
from db_utils import get_db
from engine.background_tasks import analyze_and_cache_plot

# Keeps track of the last processed boundaries to prevent infinite loops
# when the backend itself updates the plot document with the 'analysis' field.
_processed_plot_hashes = {}
_debouncers = {}

def trigger_analysis_debounced(plot_id):
    """
    Waits 2 seconds before triggering analysis. If called again for the same
    plot_id within 2 seconds, the previous timer is cancelled. This prevents
    startup cascades where multiple crops trigger their parent plot simultaneously.
    """
    if plot_id in _debouncers:
        _debouncers[plot_id].cancel()
    
    def run_it():
        analyze_and_cache_plot(plot_id)
        # Cleanup
        if plot_id in _debouncers:
            _debouncers.pop(plot_id, None)

    t = threading.Timer(2.0, run_it)
    _debouncers[plot_id] = t
    t.start()

def start_firestore_listeners():
    print("[Listeners] Starting Realtime Firestore Listeners...")
    db = get_db()
    if not db:
        print("[Listeners] Failed to get DB connection. Cannot start listeners.")
        return

    # Watch Plots
    plots_ref = db.collection('plots')
    plots_watch = plots_ref.on_snapshot(_on_plots_snapshot)

    # Watch Crops (Notice: using collection_group to catch all crops across all plots)
    # This requires a composite index in Firestore if combined with filters, 
    # but a bare collection_group query works out of the box.
    crops_watch = db.collection_group('crops').on_snapshot(_on_crops_snapshot)
    
    # Store references so they don't get garbage collected
    return plots_watch, crops_watch


def _on_plots_snapshot(col_snapshot, changes, read_time):
    print(f"[Listeners] Detected {len(changes)} plot changes.")
    for change in changes:
        plot_doc = change.document
        plot_id = plot_doc.id
        plot_data = plot_doc.to_dict()

        if change.type.name in ['ADDED', 'MODIFIED']:
            boundaries = plot_data.get('boundaries')
            if not boundaries:
                continue
                
            # Create a simple hash of the boundaries to detect if they *actually* changed
            # (Firestore triggers MODIFIED even if we only updated the 'analysis' field)
            try:
                b_str = json.dumps(boundaries, sort_keys=True)
                b_hash = hashlib.md5(b_str.encode()).hexdigest()
            except:
                b_hash = str(boundaries)

            # Prevent infinite loops: If we already analyzed this exact geometry, skip.
            # However, if it's 'ADDED' and doesn't have an 'analysis' field yet, we must analyze it.
            has_analysis = 'analysis' in plot_data
            
            if _processed_plot_hashes.get(plot_id) == b_hash and has_analysis:
                # The geometry hasn't changed. This MODIFIED event was likely 
                # triggered by our own backend writing the analysis field. Ignore it!
                continue

            _processed_plot_hashes[plot_id] = b_hash
            
            print(f"[Listeners] Triggering debounced background analysis for Plot: {plot_id}")
            trigger_analysis_debounced(plot_id)


def _on_crops_snapshot(col_snapshot, changes, read_time):
    print(f"[Listeners] Detected {len(changes)} crop changes.")
    for change in changes:
        if change.type.name in ['ADDED', 'MODIFIED', 'REMOVED']:
            crop_doc = change.document
            
            # Find the parent plot ID
            # crop_doc.reference path is: plots/{plot_id}/crops/{crop_id}
            parent_plot_ref = crop_doc.reference.parent.parent
            if parent_plot_ref:
                plot_id = parent_plot_ref.id
                print(f"[Listeners] Crop changed. Triggering debounced analysis update for parent Plot: {plot_id}")
                trigger_analysis_debounced(plot_id)
