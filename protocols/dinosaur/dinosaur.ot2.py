from opentrons import labware, instruments
from otcustomizers import StringSelection

metadata = {
    'protocolName': 'Dinosaur Demo',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library'
    }

# a 12 row trough for sources
trough = labware.load('trough-12row', 8)

# plate to create dinosaur in
plate = labware.load('96-PCR-flat', 3)

# a tip rack for our pipette
p200rack = labware.load('tiprack-200ul', 6)

# wells to dispense dinosaur body in green
green_wells = [
    well.bottom() for well in plate.wells(
        'E1', 'D2', 'E2', 'D3', 'E3', 'F3', 'G3', 'H3',
        'C4', 'D4', 'E4', 'F4', 'G4', 'H4', 'C5', 'D5',
        'E5', 'F5', 'G5', 'C6', 'D6', 'E6', 'F6', 'G6',
        'C7', 'D7', 'E7', 'F7', 'G7', 'D8', 'E8', 'F8',
        'G8', 'H8', 'E9', 'F9', 'G9', 'H9', 'F10', 'G11',
        'H12')]

# wells to dispense dinosaur back plates in blue
blue_wells = [
    well.bottom() for well in plate.wells(
        'C3', 'B4', 'A5', 'B5', 'B6', 'A7', 'B7',
        'C8', 'C9', 'D9', 'E10', 'E11', 'F11', 'G12')]

# green solution location
green = trough.wells('A1')
# blue solution location
blue = trough.wells('A2')


def run_custom_protocol(
        pipette_axis: StringSelection(
            'left', 'right')='left'):

    p300 = instruments.P300_Single(
        mount=pipette_axis,
        tip_racks=[p200rack]
    )

    # macro commands like .distribute() make writing long sequences easier:
    # distribute green solution to the body
    p300.distribute(50, green, green_wells, disposal_vol=0, blow_out=True)
    # distribute blue solution to the dinosaur's back
    p300.distribute(50, blue, blue_wells, disposal_vol=0, blow_out=True)
