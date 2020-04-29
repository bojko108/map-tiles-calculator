import math

# http://stefanosabatini.eu/tools/tilecalc/
# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers
# https://tools.geofabrik.de/calc/#type=geofabrik_standard&bbox=23.3579,42.2955,24.7314,43.2964


class Calculator:
    def __init__(self, minZoom=1, maxZoom=20, tileSize=256):
        '''
        Creates a new Map Tiles Calcualtor object

        Parameters
        ----------
        minZoom (int): Start zoom level
        
        maxZoom (int): End zoom level
        
        tileSize (int): Tile size (not used for now!)

        Attributes
        ----------
        minZoom (int): Start zoom level
        
        maxZoom (int): End zoom level
        
        tileSize (int): Tile size (not used for now!)
        '''
        self.minZoom = minZoom
        self.maxZoom = maxZoom
        # in pixels
        self.tileSize = tileSize

    def calculateTileCount(self, bbox, minZoom=0, maxZoom=0):
        '''
        Calculates estimated map tiles count for a specific bounding box

        Parameters
        ----------
        bbox (Array<double>): Area for which to calculate map tiles count

        minZoom (int): Start zoom level
        
        maxZoom (int): End zoom level

        Returns
        ----------
        count : int
            Estimated map tiles count
        '''
        minZoom = minZoom if minZoom > 0 else self.minZoom
        maxZoom = maxZoom if maxZoom > 0 else self.maxZoom

        tileCount = 0
        for zoom in range(minZoom, maxZoom + 1):
            lowerLeftTile = self.latLon2tileCoords(bbox[1], bbox[0], zoom)
            upperRightTile = self.latLon2tileCoords(bbox[3], bbox[2], zoom)

            # WORKING:
            columns = upperRightTile[1] - lowerLeftTile[1] + 1
            rows = lowerLeftTile[2] - upperRightTile[2] + 1
            tileCount += columns * rows

            # WORKING:
            # for c in range(lowerLeftTile[1], upperRightTile[1] + 1):
            #     for r in range(upperRightTile[2], lowerLeftTile[2] + 1):
            #         tileCount += 1

        return tileCount

    def latLon2tileCoords(self, lat_deg, lon_deg, zoom):
        '''
        Calculates tile coordinates from geographic coordinates

        Parameters
        ----------
        lat_deg (double): Geographic latitude

        lon_deg (double): Geographic longitude
        
        zoom (int): Zoom level

        Returns
        ----------
        tileCoordinates : Array<int>
            Tile coordinates: zoom, x, y
        '''
        lat_rad = math.radians(lat_deg)
        n = 2.0**zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (zoom, xtile, ytile)

    def tileCoords2LatLon(self, zoom, xtile, ytile):
        '''
        Calculates geographic coordinates from tile coordinates

        Parameters
        ----------
        zoom (int): Tile zoom level

        xtile (int): Tile column
        
        ytile (int): Tile row

        Returns
        ----------
        latLon (Array<double>): Geographic coordinates: lat, lon
        '''
        n = 2.0**zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)