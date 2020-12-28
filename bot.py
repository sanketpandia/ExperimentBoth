import discord
from discord.ext import commands
import json
import airtable_connection
from dotenv import load_dotenv
import cmflight_instructors as cm

env = load_dotenv(dotenv_path="./.env")

import os

client = commands.Bot(command_prefix=">")
json_data = {}
with open('./aircraft-performances.json') as jsonf:
    json_data = json.load(jsonf)


@client.event
async def on_ready():
    print("Bot is ready. Logged in as {0.user}".format(client))


keyword = "AIRCRAFT PERFORMANCE"


def get_aircraft(message):
    aircrafts_listed = json_data["keys"]
    aircraft_flag = False
    message = message.upper()
    for aircraft in aircrafts_listed:
        if aircraft.upper() in message:
            return aircraft

    return ""


def show_table(table):
    string = ''
    for line in table:
        string += '| {} '.format(line)
        string += '|\n'

    return string


def get_aircraft_list_string():
    aircraft_listed = json_data["keys"]

    aircraft_listed_str = ""
    counter = 2
    for plane in aircraft_listed:
        aircraft_listed_str = aircraft_listed_str + str(plane)

        if counter == 3:
            counter = 1
            aircraft_listed_str = aircraft_listed_str + "\n"
        else:
            empty_spaces = 50 - len(plane)

            aircraft_listed_str = aircraft_listed_str + empty_spaces * " "

        counter = counter + 1

    return "Sorry I couldn't recognise it. Try one from this list\n" + aircraft_listed_str


def get_optimised_aircraft_string(aircraft_data):
    aircraft_data_string = """
    **Aircraft**: {}                Flight Ceiling: {}
    MTOW: {}                    MLW: {}
    V2: {}                      VS: {}
    Climb: 
    5000ft: {}
    15000ft: {}
    24000ft: {}
    Mach climb: {}
    Cruise Speed: {}            Typical Range: {}
    Descent:
    Descent to 24000ft: {}      Descent to 10000ft: {}
    Approach / MCS: {}
    Landing Speed: {}
    Flap Speeds: {}
    """
    return aircraft_data_string.format(aircraft_data["Airplane"], aircraft_data["Ceiling"], aircraft_data["MTOW"],
                                       aircraft_data["MLW"], aircraft_data["V2"], aircraft_data["VS"],
                                       aircraft_data["Climb to 5000ft"], aircraft_data["Climb to 15000ft"],
                                       aircraft_data["Climb to 24000ft"], aircraft_data["Mach Climb"],
                                       aircraft_data["Cruise speed"], aircraft_data["Typical Range"],
                                       aircraft_data["Descend to 24000ft"], aircraft_data["Descend to 10000ft"],
                                       aircraft_data["Approach / MCS"], aircraft_data["Landing"],
                                       aircraft_data["Flaps at descend"])


@client.command(name="aircraft")
async def get_airplanes(ctx, args):
    aircraft = get_aircraft(args)
    get_aircraft_list_string()
    if aircraft == "":
        await ctx.send(get_aircraft_list_string())
    else:
        await ctx.send(get_optimised_aircraft_string(json_data[aircraft]))


@client.command(name="cm_flightlines")
async def get_flightlines(ctx, args):
    flightlines = airtable_connection.get_flightlines(args)
    if len(flightlines) == 0:
        await ctx.send("Art thou sure you have thy callsign correct?")
    else:
        await ctx.send("Here art thy flight lines: \n" + flightlines)


@client.command(name="cm_time")
async def get_cm_time(ctx, args):
    flightlines = airtable_connection.get_time(args)
    if len(flightlines) == 0:
        await ctx.send("Your record seems to be misplaced/ unavailable. Or might be something wrong with me :cry:")
    else:
        await ctx.send(flightlines)


@client.command(name="cm_pirep")
async def file_pirep(ctx, *args):
    if len(args)==0:
        await ctx.send("Use the format to file a CM Pirep: \nAFKLMxxx airline_KLM aircraft_B777-300ER route_EHAM-OMDB ft_06:30 pax_240 cargo_4500 fuel_35000")
    else:
        await ctx.send("Functionality not updated yet")

@client.command(name="cm_unassigned")
async def get_unassigned(ctx):
    flightlines = cm.get_unassigned()
    if len(flightlines) == 0:
        await ctx.send("Unable to find any unassigned pilots. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the unassigned pilots" + flightlines)

@client.command(name="cm_my_trainee")
async def get_assigned(ctx, args):
    flightlines = cm.get_typeratings_by_region(args)
    if len(flightlines) == 0:
        await ctx.send("Unable to find any assigned pilots to this region. Or might be something is wrong with me :cry:")
    else:
        await ctx.send("Here are the pilots assigned to this region/ FI \n" + flightlines)

client.run(os.getenv("BOT_ID"))
