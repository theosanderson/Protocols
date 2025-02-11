from opentrons import containers, instruments
from otcustomizers import FileInput, StringSelection

tiprack_slots = ['D1', 'A2', 'C2', 'E2']
tipracks = [containers.load('tiprack-200ul', slot) for slot in tiprack_slots]
trash = containers.load('trash-box', 'E1')

example_csv = """
A1, 20
A3, 10
B2, 15

"""


def run_custom_protocol(
        volumes_csv: FileInput=example_csv,
        pipette_axis: StringSelection(
            'B (left side)', 'A (right side)')='B (left side)',
        pipette_model: StringSelection(
            'p300', 'p50', 'p10', 'p1000')='p300',
        source_plate_type: StringSelection('96-flat', '384-plate')='96-flat',
        destination_plate_type: StringSelection(
            '96-flat', '384-plate')='96-flat',
        tip_reuse: StringSelection(
            'new tip each time', 'reuse tip')='new tip each time'
        ):

    pipette_max_vol = int(pipette_model[1:])

    pipette = instruments.Pipette(
        axis='b' if pipette_axis[0] == 'B' else 'a',
        max_volume=pipette_max_vol,
        min_volume=pipette_max_vol / 10,
        tip_racks=tipracks,
        trash_container=trash
    )

    data = [
        [well, vol]
        for well, vol in
        [row.split(',') for row in volumes_csv.strip().splitlines() if row]
    ]

    source_plate = containers.load(source_plate_type, 'B1')
    dest_plate = containers.load(destination_plate_type, 'C1')

    tip_strategy = 'always' if tip_reuse == 'new tip each time' else 'once'
    for well_idx, (source_well, vol) in enumerate(data):
        if source_well and vol:
            vol = float(vol)
            pipette.transfer(
                vol,
                source_plate.wells(source_well),
                dest_plate(well_idx),
                new_tip=tip_strategy)
