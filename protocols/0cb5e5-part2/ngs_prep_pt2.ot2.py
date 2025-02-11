from opentrons import labware, instruments, modules, robot
from otcustomizers import StringSelection
import math

metadata = {
    'protocolName': 'NGS Library Prep Part 2/4: M3 Second Strand Synthesis \
and M4 DNA Cleanup',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request'
}

# create custom plate
plate_name = 'Abgene-MIDI-96-800ul'
if plate_name not in labware.list():
    labware.create(
        plate_name,
        grid=(12, 8),
        spacing=(9, 9),
        diameter=7,
        depth=27,
        volume=800
    )

# load modules and labware
magdeck = modules.load('magdeck', '1')
magplate = labware.load(plate_name, '1', share=True)
trough = labware.load('usascientific_12_reservoir_22ml', '2')
tempdeck = modules.load('tempdeck', '4')
plate_TM = labware.load(
    'opentrons_96_aluminumblock_biorad_wellplate_200ul', '4', share=True)
tempdeck.set_temperature(25)
tempdeck.wait_for_temp()
reagent_plate = labware.load(
    'opentrons_96_aluminumblock_biorad_wellplate_200ul', '5', 'reagent plate')
plate_2 = labware.load(
    'opentrons_96_aluminumblock_biorad_wellplate_200ul', '7')
tips10 = [labware.load('tiprack-10ul', slot)
          for slot in ['3', '6', '8']]
tips300 = [labware.load('opentrons-tiprack-300ul', str(slot))
           for slot in range(9, 12)]


def run_custom_protocol(
        number_of_samples: int = 96,
        p10_multi_mount: StringSelection('right', 'left') = 'right',
        p300_multi_mount: StringSelection('left', 'right') = 'left',
        reagent_starting_column: int = 1
):
    # checks
    if number_of_samples > 96 or number_of_samples < 1:
        raise Exception('Invalid number of samples')
    if p10_multi_mount == p300_multi_mount:
        raise Exception('Invalid pipette mount combination')
    if reagent_starting_column > 7:
        raise Exception('Invlaid reagent starting column')

    # pipettes
    m10 = instruments.P10_Multi(mount=p10_multi_mount, tip_racks=tips10)
    m300 = instruments.P300_Multi(mount=p300_multi_mount, tip_racks=tips300)

    # reagent setup
    [fs2e1, fs1, rs, ss1, ss2e2, pcre3] = [
        reagent_plate.rows('A')[ind]
        for ind in range(reagent_starting_column-1, reagent_starting_column+5)
    ]
    [pb, eb, ps] = [trough.wells(ind) for ind in range(3)]
    etoh = [chan for chan in trough.wells('A4', length=4)]
    etoh_waste = [chan for chan in trough.wells('A8', length=4)]
    liquid_waste = trough.wells('A12')

    # sample setup
    num_cols = math.ceil(number_of_samples/8)
    samples_TM = plate_TM.rows('A')[:num_cols]
    samples_2 = plate_2.rows('A')[:num_cols]
    samples_mag = magplate.rows('A')[:num_cols]

    # tip check function
    tip10_max = len(tips10)*12
    tip300_max = len(tips300)*12
    tip10_count = 0
    tip300_count = 0

    def tip_check(pipette):
        nonlocal tip10_count
        nonlocal tip300_count
        if pipette == 'p300':
            tip300_count += 1
            if tip300_count > tip300_max:
                m300.reset()
                tip300_count = 1
                robot.pause('Please replace 300ul tipracks before resuming.')
        else:
            tip10_count += 1
            if tip10_count > tip10_max:
                m10.reset()
                tip10_count = 1
                robot.pause('Please replace 10ul tipracks before resuming.')

    def etoh_wash(inds):
        for wash in inds:
            tip_check('p300')
            m300.pick_up_tip()
            m300.transfer(
                120,
                etoh[wash],
                [s.top() for s in samples_mag],
                new_tip='never'
            )
            m300.delay(seconds=30)
            for s in samples_mag:
                if not m300.tip_attached:
                    tip_check('p300')
                    m300.pick_up_tip()
                m300.transfer(120, s, etoh_waste[wash], new_tip='never')
                m300.drop_tip()

    """M3 Second Strand Synthesis"""

    for s in samples_TM:
        tip_check('p300')
        m300.pick_up_tip()
        m300.transfer(10, ss1, s, new_tip='never')
        m300.mix(10, 25, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    robot.pause('Seal the plate and put it on a thermocycler for 98°C/1min; \
ramp down to 25°C; 25°C/30min. Then unseal and replace it on tempdeck in slot \
4. Place a new MIDI plate on the magdeck. Place a new PCR plate in slot 7.')

    for s in samples_TM:
        tip_check('p300')
        m300.pick_up_tip()
        m300.transfer(5, ss2e2, s, new_tip='never')
        m300.mix(10, 30, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=15)

    """M4 DNA Cleanup"""

    tip_check('p300')
    m300.pick_up_tip()
    m300.mix(10, 40, pb)
    m300.blow_out(pb.top())
    m300.distribute(
        16, pb, [s for s in samples_mag], disposal_vol=0, new_tip='never')

    for source, dest in zip(samples_TM, samples_mag):
        if not m300.tip_attached:
            tip_check('p300')
            m300.pick_up_tip()
        m300.transfer(35, source, dest, new_tip='never')
        m300.mix(15, 40, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=5)
    robot._driver.run_flag.wait()
    magdeck.engage(height=18)
    m300.delay(minutes=3)

    for s in samples_mag:
        tip_check('p300')
        m300.transfer(51, s, liquid_waste)

    magdeck.disengage()

    for s in samples_mag:
        tip_check('p300')
        m300.pick_up_tip()
        m300.transfer(40, eb, s, new_tip='never')
        m300.mix(15, 30, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=2)

    for s in samples_mag:
        tip_check('p300')
        m300.pick_up_tip()
        m300.transfer(48, ps, s, new_tip='never')
        m300.mix(15, 45, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=5)
    robot._driver.run_flag.wait()
    magdeck.engage(height=18)
    m300.delay(minutes=3)

    for s in samples_mag:
        tip_check('p300')
        m300.transfer(96, s, liquid_waste)

    etoh_wash(range(2))

    m300.delay(minutes=5)

    magdeck.disengage()

    for s in samples_mag:
        tip_check('p300')
        m300.pick_up_tip()
        m300.transfer(20, eb, s, new_tip='never')
        m300.mix(15, 15, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=2)
    robot._driver.run_flag.wait()
    magdeck.engage(height=18)
    m300.delay(minutes=3)

    for source, dest in zip(samples_mag, samples_2):
        tip_check('p300')
        m300.transfer(17, source, dest, blow_out=True)

    magdeck.disengage()

    robot.comment('Proceed with Part 3/4: M5 PCR Amplification')
