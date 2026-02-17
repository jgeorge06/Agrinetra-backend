# Agrinetra Database Schema

## Active Tables

### 1. Plots
Stores information about agricultural plots.

```sql
CREATE TABLE `plots` (
  `pid` varchar(36) NOT NULL,
  `uid` varchar(255) DEFAULT NULL,
  `boundaries` json DEFAULT NULL,
  `plotname` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
- **pid**: Plot ID (String/Varchar).
- **uid**: User ID (String/Varchar, from Firebase).
- **plotname**: Name given to the plot.
- **boundaries**: JSON array of coordinates.

### 2. Crops
Stores information about crops planted in plots.

```sql
CREATE TABLE `crops` (
  `pid` varchar(36) DEFAULT NULL,
  `cropname` varchar(20) DEFAULT NULL,
  `plantingdate` date DEFAULT NULL,
  `harvestdate` date DEFAULT NULL,
  KEY `pid` (`pid`),
  CONSTRAINT `crops_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `plots` (`pid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
- **pid**: Foreign Key linking to `Plots.pid`.
- **cropname**: Name of the crop.
- **plantingdate**: Date planted.
- **harvestdate**: Expected harvest date.

## Inactive / Future Tables (Not currently used by Backend)

### 3. Sensors
Stores metadata about IoT sensors installed in plots.

```sql
CREATE TABLE `sensors` (
  `sid` int NOT NULL,
  `pid` varchar(36) DEFAULT NULL,
  `latitude` decimal(10,0) DEFAULT NULL,
  `longitude` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`sid`),
  KEY `pid` (`pid`),
  CONSTRAINT `sensors_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `plots` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
- **sid**: Sensor ID (Integer, Primary Key).
- **pid**: Plot ID where the sensor is located.
- **latitude/longitude**: GPS coordinates of the sensor.

### 4. Datas
Stores time-series data collected from sensors.

```sql
CREATE TABLE `datas` (
  `sid` int DEFAULT NULL,
  `recordtime` datetime DEFAULT NULL,
  `moisture` int DEFAULT NULL,
  `tempreature` int DEFAULT NULL,
  `humidity` int DEFAULT NULL,
  KEY `sid` (`sid`),
  CONSTRAINT `datas_ibfk_1` FOREIGN KEY (`sid`) REFERENCES `sensors` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
- **sid**: Sensor ID (Foreign Key).
- **recordtime**: Timestamp of the reading.
- **moisture/tempreature/humidity**: Sensor readings.
