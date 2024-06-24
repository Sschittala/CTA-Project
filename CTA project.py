#
# header comment! Overview, name, etc.
# Overview: Inputs commands from the user and outputs data from the CTA database. SQL is used to retrieve the data, while python is used to display the results
# Name: Sai Chittala
# Date: 01/31/2024
#


import sqlite3
import matplotlib.pyplot as plt
import math

##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General Statistics:")
    # data for number of stations
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone();
    print("  # of stations:", f"{row[0]:,}")

    # data for number of stops
    dbCursor.execute("Select count(*) From Stops;")
    row = dbCursor.fetchone();
    print("  # of stops:", f"{row[0]:,}")

    # data for the number of riders
    dbCursor.execute("Select count(*) From Ridership;")
    row = dbCursor.fetchone();
    print("  # of ride entries:", f"{row[0]:,}")

    # data for the date ranges
    dbCursor.execute("Select strftime('%Y-%m-%d', MIN(Ride_Date)), strftime('%Y-%m-%d',MAX(Ride_Date)) From Ridership;")
    row = dbCursor.fetchone();
    print("  date range:", row[0], "-", row[1])

    # data for the total riders
    dbCursor.execute("Select SUM(Num_Riders) From Ridership;")
    row = dbCursor.fetchone();
    print("  Total ridership:", f"{row[0]:,}")

# Command 1
# Find all the station names that matches the user input
def station_match(dbConn, partialStation_name):
    dbCursor = dbConn.cursor()

    # Retrieves the station_id and the station name from the database to match the user input
    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC",
                     (f"{partialStation_name}",))
    rows = dbCursor.fetchall()
    if rows:
        for row in rows:
            print(f"{row[0]} : {row[1]}")
    else:
        print("**No stations found...")

# Command 2
# Finds the percentages of the riders on weekdays, Saturdays, sundays/holidays
def get_percentages(dbConn, station_name):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = (SELECT Station_ID FROM Stations WHERE Station_Name = ?)", (station_name,))
    tot_ridership = dbCursor.fetchone()[0]
    if tot_ridership is None:
        print(f"**No data found...")
        return None, None, None

    # retrieves the Ridership total for weekday
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = (SELECT Station_ID FROM Stations WHERE Station_Name = ?) AND Type_of_Day = 'W'",(station_name,))
    weekday_total = dbCursor.fetchone()[0]

    # retrieves the ridership total for saturday
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = (SELECT Station_ID FROM Stations WHERE Station_Name = ?) AND Type_of_Day = 'A'",(station_name,))
    saturday_total = dbCursor.fetchone()[0]

    # retrieves the ridership total for sunday/holiday
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = (SELECT Station_ID FROM Stations WHERE Station_Name = ?) AND Type_of_Day = 'U'",(station_name,))
    sunday_total = dbCursor.fetchone()[0]

    # Outputs the data for the valid user input station
    if tot_ridership  > 0:
        weekday_percent = (weekday_total / tot_ridership) * 100
        saturday_percent = (saturday_total / tot_ridership) * 100
        sunday_percent = (sunday_total / tot_ridership) * 100
        print(f"Percentage of ridership for the {station_name} station:")
        print("  Weekday Ridership:", f"{weekday_total:,}", f"({weekday_percent:.2f}%)")
        print("  Saturday Ridership:", f"{saturday_total:,}", f"({saturday_percent:.2f}%)")
        print("  Sunday/holiday Ridership:", f"{sunday_total:,}", f"({sunday_percent:.2f}%)")
        print("  Total ridership:", f"{tot_ridership:,}")
    else:
        print("**No data found...")

# Command 3
# Outputs the data for the total ridership on weekdays for each station with station names
def get_weekday_ridership(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("""SELECT Stations.Station_Name, SUM(Ridership.Num_Riders) AS tot_riders FROM Ridership
    INNER JOIN Stations ON Ridership.Station_ID = Stations.Station_ID WHERE Ridership.Type_of_Day = 'W'
    GROUP BY Stations.Station_Name
    ORDER BY tot_riders DESC""")
    return dbCursor.fetchall()

# helper function for command 3 that displays the info
def display_info(weekday_totals):
    print("Ridership on Weekdays for each station")
    if weekday_totals:
        total_weekday = sum(row[1] for row in weekday_totals)
        for stations, ridership in weekday_totals:
            percentage = (ridership / total_weekday) * 100
            print(f"{stations} : {ridership:,} ({percentage:.2f}%)")
    else:
        print("No data found for weekday ridership.")

# Command 4
# Outputs all the stops for the user inputted line color in that direction
def stops_for_lineColor_Direction(dbConn):
    dbCursor = dbConn.cursor()
    line_input = input("\nEnter a line color (e.g. Red or Yellow): ")
    line_input = line_input.upper()
    dbCursor.execute("""SELECT Stop_Name,ADA FROM Stops JOIN StopDetails ON 
                     Stops.Stop_ID = StopDetails.Stop_ID JOIN Lines ON
                     StopDetails.Line_ID = Lines.Line_ID WHERE UPPER(Lines.Color) = ?
                     GROUP BY Stop_Name ORDER BY Stop_Name ASC;""",(line_input,))
    num_rows = dbCursor.fetchall();
    if num_rows:
        line_direction = input("Enter a direction (N/S/W/E): ")
        line_direction = line_direction.upper()
        dbCursor.execute("""SELECT Stop_Name, ADA FROM Stops JOIN StopDetails ON
                             Stops.Stop_ID = StopDetails.Stop_ID JOIN Lines ON
                             StopDetails.Line_ID = Lines.Line_ID WHERE UPPER(Lines.Color) = ? AND UPPER(Stops.Direction) = ?\
                             GROUP BY Stop_Name ORDER BY Stop_Name ASC;""", (line_input,line_direction))
        num_rows = dbCursor.fetchall();
        if num_rows:
            for row in num_rows:
                if(row[1]==1):
                    print(row[0],": direction = ",line_direction," (handicap accessible)")
                else:
                    print(row[0], ": direction = ", line_direction," (not handicap accessible)")
        else:
            print("**That line does not run in the direction chosen...")
    else:
        print("**No such line...")

# Command 5
# Outputs the number of stops for each line color, separated by direction
def num_of_stops_line_color(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("""SELECT Lines.Color, Stops.Direction, COUNT(Stops.Stop_ID) AS num_stops FROM Stops
                    INNER JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
                    INNER JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
                    GROUP BY Lines.Color, Stops.Direction
                    ORDER BY Lines.Color ASC, Stops.Direction ASC
                    """)
    tot_stops = dbCursor.fetchall()
    dbCursor.execute("SELECT COUNT(*) FROM Stops")
    tot_num_stops = dbCursor.fetchone()[0]
    if tot_num_stops > 0:
        print("Number of Stops For Each Color By Direction")
        for line_color, line_direction, num_stops in tot_stops:
            percent = (num_stops / tot_num_stops) * 100
            print(f"{line_color} going {line_direction} : {num_stops} ({percent:.2f}%)")
    else:
        print("No stops found")

# Command 6
# Outputs the total ridership for each year for that station
def total_ridership_year(dbConn):
    dbCursor = dbConn.cursor()
    station_name = input("\nEnter a station name (wildcards _ and %): ")
    dbCursor.execute("SELECT Station_Name FROM Stations WHERE Station_Name LIKE ?", (station_name,))
    rows = dbCursor.fetchall()
    if not rows:
        print("**No station found...")
        return
    elif len(rows) > 1:
        print("**Multiple stations found...")
        return
    else:
        station_name = rows[0][0]
        dbCursor.execute("""SELECT strftime('%Y', Ride_Date) AS year_ride, SUM(Num_Riders) AS tot_riders FROM Ridership
                         JOIN Stations ON Ridership.Station_ID = Stations.Station_ID WHERE Stations.Station_Name LIKE ? GROUP BY year_ride 
                         ORDER BY year_ride ASC""", (f"{station_name}",))
    ridership_data = dbCursor.fetchall()
    if not ridership_data:
        print("**No ridership data found for the station and year...")
    else:
        print(f"Yearly Ridership at {station_name}")
        for ride_year, tot_ridership in ridership_data:
            print(f"{ride_year} : {tot_ridership:,}")
    plot_question = input("Plot? (y/n) ")
    if plot_question.lower() == 'y':
        plot_data(ridership_data, station_name)

# Plots the data for command 6
def plot_data(ridership_data, station_name):
    years = [row[0] for row in ridership_data]
    tot_ridership = [row[1] for row in ridership_data]
    plt.figure(figsize=(10, 6))
    plt.plot(years, tot_ridership)
    plt.title(f"Yearly Ridership at {station_name}")
    plt.xlabel("Year")
    plt.ylabel("Number of Riders")
    plt.grid(True)
    plt.show()

# Command 7
# Outputs the total ridership for each month in the year based on the user inputted station name and year
def ridership_each_month(dbConn):
    dbCursor = dbConn.cursor()
    station_name = input("\nEnter a station name (wildcards _ and %): ")
    dbCursor.execute("SELECT Station_Name from Stations where Stations.Station_Name like ?;",(station_name,))
    num_rows = dbCursor.fetchall();
    if num_rows:
        if(len(num_rows)==1):
            save_station_name = num_rows[0][0]
            ride_date = input("Enter a year: ")
            query = ("""SELECT strfTime('%m/%Y',Ride_Date) AS num_date,SUM(Num_Riders) FROM Ridership JOIN Stations
                             ON Ridership.Station_ID = Stations.Station_ID
                            WHERE Stations.Station_Name LIKE ? AND strftime('%Y', Ridership.Ride_Date) = ? GROUP BY num_date ORDER BY num_date ASC;""")
            dbCursor.execute(query, (station_name,ride_date,))
            num_rows = dbCursor.fetchall();
            print("Monthly Ridership at ",save_station_name," for ",ride_date)
            for row in num_rows:
                print(row[0]," : ",f"{row[1]:,}")
            plotChoice = input("Plot? (y/n) ")
            if plotChoice == "y":
                x=[]
                y=[]
                month = 1
                for row in num_rows:
                    x.append(month)
                    y.append(row[1])
                    month = month+1
                plt.xlabel("Month")
                plt.ylabel("Number of Riders")
                plt.title(f"Monthly Ridership at {save_station_name} ({ride_date})")
                plt.ioff()
                plt.plot(x, y)
                plt.show()


        else:
            print("**Multiple stations found...")


    else:
        print("**No station found...")


# Command 8
# Outputs the total ridership for the two stations and for each day in the year that is provided by the user
def tot_ridership_days(dbConn):
    dbCursor = dbConn.cursor()
    year_compare = input("\nYear to compare against? ")
    station_1 = input("\nEnter station 1 (wildcards _ and %): ")
    dbCursor.execute("SELECT Station_Name FROM Stations WHERE Stations.Station_Name LIKE ?;", (station_1,))
    num_rows = dbCursor.fetchall()
    if num_rows:
        if (len(num_rows) == 1):
            station_2 = input("\nEnter station 2 (wildcards _ and %): ")
            dbCursor.execute("SELECT Station_Name FROM Stations WHERE Stations.Station_Name LIKE ?;", (station_2,))
            num_rows_2 = dbCursor.fetchall()
            if num_rows_2:
                if(len(num_rows_2)==1):
                    station_list(num_rows[0][0],year_compare,1,dbConn)
                    station_list(num_rows_2[0][0],year_compare,2,dbConn)
                    plot_question = input("\nPlot? (y/n) ")
                    if plot_question == "y":
                        x = []
                        y = []
                        query1 = ("""SELECT strfTime('%Y-%m-%d',Ride_Date) AS num_date,SUM(Num_Riders) FROM Ridership JOIN Stations 
                                            ON Ridership.Station_ID = Stations.Station_ID 
                                            WHERE Stations.Station_Name LIKE ? 
                                            AND strftime('%Y', Ridership.Ride_Date) = ? GROUP BY num_date ORDER BY num_date ASC;""")
                        dbCursor.execute(query1, (station_1, year_compare,))
                        station1_data = dbCursor.fetchall()
                        day = 0
                        for row in station1_data:
                            day = day+1
                            x.append(day)
                            y.append(row[1])
                        query2 = ("""SELECT strfTime('%Y-%m-%d',Ride_Date) AS num_date2,SUM(Num_Riders) FROM Ridership JOIN Stations 
                                            ON Ridership.Station_ID = Stations.Station_ID 
                                            WHERE Stations.Station_Name LIKE ? 
                                            AND strftime('%Y', Ridership.Ride_Date) = ? GROUP BY num_date2 ORDER BY num_date2 ASC;""")
                        dbCursor.execute(query2, (station_2, year_compare,))
                        station2_data = dbCursor.fetchall()
                        y2 = []
                        for row in station2_data:
                            y2.append(row[1])

                        plt.xlabel("Day")
                        plt.ylabel("Number of Riders")
                        plt.title(f"Ridership each day of ({year_compare})")
                        plt.ioff()
                        plt.plot(x,y,label=num_rows[0][0])
                        plt.plot(x,y2,label=num_rows_2[0][0])
                        plt.legend(loc='upper right')
                        plt.show()



                else:
                    print("**Multiple stations found...")
            else:
                print("**No station found...")

        else:
            print("**Multiple stations found...")
    else:
        print("**No station found...")

# Helper function that lists the rider dates for the first 5 days for the given stations
def station_list(station_name,year_compare,station_num,dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT Station_ID FROM Stations WHERE Station_Name like ?;", (station_name,))
    station_name_ID = dbCursor.fetchall()
    query1 = ("""SELECT strfTime('%Y-%m-%d',Ride_Date) AS num_date,SUM(Num_Riders) FROM Ridership JOIN Stations 
                        ON Ridership.Station_ID = Stations.Station_ID 
                        WHERE Stations.Station_Name LIKE ? 
                        AND strftime('%Y', Ridership.Ride_Date) = ? GROUP BY num_date ORDER BY num_date ASC limit 5;""")
    dbCursor.execute(query1, (station_name, year_compare,))
    station_start_Dates = dbCursor.fetchall()
    query2 = ("""SELECT strfTime('%Y-%m-%d',Ride_Date) AS num_date2,SUM(Num_Riders) FROM Ridership JOIN Stations 
                        ON Ridership.Station_ID = Stations.Station_ID 
                        WHERE Stations.Station_Name LIKE ? 
                        AND strftime('%Y', Ridership.Ride_Date) = ? GROUP BY num_date2 ORDER BY num_date2 DESC limit 5;""")
    dbCursor.execute(query2, (station_name, year_compare,))
    station_end_dates = dbCursor.fetchall()
    print(f"Station {station_num}: {station_name_ID[0][0]} {station_name}")
    for row in station_start_Dates:
        print(f"{row[0]}  {row[1]}")
    for row in reversed(station_end_dates):
        print(f"{row[0]}  {row[1]}")

# Command 9
# Outputs all the stations within a one mile square radius based on the set of latitude and longitudes given by the user

def stations_in_a_mile_radius(dbConn):
    try:
        user_latitude = float(input("\nEnter a latitude: "))
        if not 40 <= user_latitude <= 43:
            print("**Latitude entered is out of bounds...")
            return

        user_longitude = float(input("Enter a longitude: "))
        if not -88 <= user_longitude <= -87:
            print("**Longitude entered is out of bounds...")
            return

        deg_of_lat = 1 / 69
        deg_of_long = 1 / 51

        upper_lat = round(user_latitude + deg_of_lat, 3)
        lower_lat = round(user_latitude - deg_of_lat, 3)
        upper_long = round(user_longitude + deg_of_long, 3)
        lower_long = round(user_longitude - deg_of_long, 3)

        dbCursor = dbConn.cursor()
        dbCursor.execute("""
        SELECT DISTINCT Stations.Station_Name, Stops.Latitude, Stops.Longitude
        FROM Stations
        LEFT JOIN Stops ON Stations.Station_ID = Stops.Station_ID
        WHERE Stops.Latitude BETWEEN ? AND ? AND Stops.Longitude BETWEEN ? AND ? 
        ORDER BY Stations.Station_Name;
        """, (lower_lat, upper_lat, lower_long, upper_long))
        num_stations = dbCursor.fetchall()

        if not num_stations:
            print("**No stations found...")
            return

        print("\nList of Stations Within a Mile")
        for station_name, latitude, longitude in num_stations:
            print(f"{station_name} : ({latitude}, {longitude})")

        plot_question = input("\nPlot? (y/n) ")
        if plot_question.lower() == 'y':
            plot_data2(num_stations)

    except ValueError:
        print("**Invalid input. Please enter a valid number.")

# Plots the data for command 9

def plot_data2(num_stations):
    image = plt.imread("chicago.png")
    x = [lon for _, _, lon in num_stations]
    y = [lat for _, lat, _ in num_stations]
    station_names = [name for name, _, _ in num_stations]

    xdims = [-87.9277, -87.5569, 41.7012, 42.0868]  # Area covered by the map
    plt.imshow(image, extent=xdims)
    if num_stations:
        plt.scatter(x, y, color='blue')
        for i, name in enumerate(station_names):
            plt.annotate(name, (x[i], y[i]))
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.title("Stations Within a Mile Radius")
    plt.show()

##################################################################
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
while True:
    print("\nPlease enter a command (1-9, x to exit): ", end = "")
    command = input().strip().lower()
    if command == 'x':
        break
    elif command == '1':
        partial_name2 = input("\nEnter partial station name (wildcards _ and %): ")
        station_match(dbConn, partial_name2)
    elif command == '2':
        station_name = input("\nEnter the name of the station you would like to analyze: ")
        get_percentages(dbConn, station_name)
    elif command == '3':
        weekday_totals = get_weekday_ridership(dbConn)
        display_info(weekday_totals)
    elif command == '4':
        stops_for_lineColor_Direction(dbConn)
    elif command == '5':
        num_of_stops_line_color(dbConn)
    elif command == '6':
        total_ridership_year(dbConn)
    elif command == '7':
        ridership_each_month(dbConn)
    elif command == '8':
        tot_ridership_days(dbConn)
    elif command == '9':
        stations_in_a_mile_radius(dbConn)
    else:
        print("**Error, unknown command, try again...")

#
# done
#


