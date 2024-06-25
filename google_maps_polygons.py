import gmplot
import webbrowser
import os
from shapely.geometry import Polygon
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to calculate the area of a polygon given its vertices using geodesic distances
def calculate_polygon_area(vertices):
    print("======================================")
    print(f"Original vertices: {vertices}")

    # Close the polygon by repeating the first coordinate at the end
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])
    
    print(f"Closed vertices: {vertices}")
    print("======================================")
    polygon = Polygon(vertices)
    if not polygon.is_valid:
        print("Invalid polygon")
        return 0

    try:
        # Calculate the area in degrees
        total_area = polygon.area
        print("======================================")
        print(f"Area in degrees: {total_area}")

        # Convert the area from degrees to square meters
        average_lat = sum(lat for lat, lon in vertices) / len(vertices)
        lat_distance = geodesic((average_lat, 0), (average_lat + 1, 0)).meters
        lon_distance = geodesic((0, vertices[0][1]), (0, vertices[0][1] + 1)).meters
        area_in_square_meters = total_area * lat_distance * lon_distance

        print(f"Polygon area in square meters: {area_in_square_meters}")
        print("======================================")
        return area_in_square_meters
    except Exception as e:
        print(f"Error calculating polygon area: {e}")
        return 0

# Function to create a Google Map with polygons
def create_google_map(polygons, api_key):
    # Center the map on the first polygon's first coordinate
    if polygons:
        center_lat, center_lng = polygons[0]["coordinates"][0]
    else:
        center_lat, center_lng = 0, 0

    gmap = gmplot.GoogleMapPlotter(center_lat, center_lng, 13, apikey=api_key)

    for polygon in polygons:
        lats, lngs = zip(*polygon["coordinates"])
        gmap.polygon(lats, lngs, color=polygon.get("color", "blue"))

    return gmap

# Input coordinates for multiple polygons
def get_polygons_from_user():
    polygons = []
    while True:
        polygon_name = input("Enter polygon name (or 'done' to finish): ")
        if polygon_name.lower() == "done":
            break

        coordinates = []
        while True:
            coord = input("Enter coordinates as 'lat,lon' (or 'done' to finish this polygon): ")
            if coord.lower() == "done":
                break
            try:
                lat, lon = map(float, coord.split(","))
                coordinates.append((lat, lon))
            except ValueError:
                print("Invalid input. Please enter coordinates in the format 'lat,lon'.")

        print(f"Coordinates for {polygon_name}: {coordinates}")

        color = input("Enter polygon color (default is 'blue'): ")
        if not color:
            color = "blue"

        area = calculate_polygon_area(coordinates)
        print(f"Calculated area for {polygon_name}: {area}")

        polygons.append({
            "name": polygon_name,
            "coordinates": coordinates,
            "color": color,
            "area": area
        })

        add_another = input("Add another polygon? (y/n): ")
        if add_another.lower() != 'y':
            break

    return polygons

# Main function
def main():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")  # Get the API key from the environment variable
    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

    polygons = get_polygons_from_user()

    gmap = create_google_map(polygons, api_key)
    output_file = "polygons_map.html"
    gmap.draw(output_file)

    # Automatically open the HTML file in a web browser
    webbrowser.open('file://' + os.path.realpath(output_file))

    # Print out the area of each polygon
    for polygon in polygons:
        print(f"The area of {polygon['name']} is {polygon['area'] / 1e6:.2f} square kilometers.")  # Convert square meters to square kilometers

if __name__ == "__main__":
    main()
