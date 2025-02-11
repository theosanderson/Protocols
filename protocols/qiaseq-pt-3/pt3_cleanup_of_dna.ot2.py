from opentrons import labware, instruments, modules, robot
from otcustomizers import StringSelection
import math

metadata = {
    'protocolName': 'QIAseq Targeted DNA Panel for Illumina Instruments Part 3:\
 Cleanup of adapter-ligated DNA',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request'
}

# load modules and labware
magdeck = modules.load('magdeck', '1')
rxn_plate = labware.load(
    'biorad_96_wellplate_200ul_pcr',
    '1',
    'reaction plate',
    share=True
)
elution_plate = labware.load(
    'opentrons_96_aluminumblock_biorad_wellplate_200ul', '2', 'elution plate')
reagent_reservoir = labware.load(
    'usascientific_12_reservoir_22ml', '3', 'reagent reservoir')

# reagents
nuc_free_water = reagent_reservoir.wells('A1')
beads = reagent_reservoir.wells('A2')
etoh = reagent_reservoir.wells('A3', length=4)
liquid_waste = [
    chan.top() for chan in reagent_reservoir.wells('A7', length=5)
]


def run_custom_protocol(
        number_of_samples: int = 96,
        p10_mount: StringSelection('right', 'left') = 'right',
        p300_mount: StringSelection('left', 'right') = 'left'
):
    # check
    if p10_mount == p300_mount:
        raise Exception('Input different mounts for pipettes.')

    num_sample_cols = math.ceil(number_of_samples/8)
    rxn_samples = rxn_plate.rows('A')[:num_sample_cols]
    elution_samples = elution_plate.rows('A')[:num_sample_cols]

    # pipettes
    tips300 = [labware.load('opentrons_96_tiprack_300ul', slot)
               for slot in ['4', '5', '6', '7']]
    tips10 = [labware.load('opentrons_96_tiprack_10ul', slot)
              for slot in ['8', '9', '10', '11']]

    m300 = instruments.P300_Multi(
        mount=p300_mount,
        tip_racks=tips300
    )
    m10 = instruments.P10_Multi(
        mount=p10_mount,
        tip_racks=tips10
    )

    tip10_count = 0
    tip300_count = 0
    tip10_max = len(tips10)*12
    tip300_max = len(tips300)*12

    def pick_up(pip):
        nonlocal tip10_count
        nonlocal tip300_count

        if pip == m10:
            if tip10_count == tip10_max:
                robot.pause('Replace 10ul tipracks before resuming.')
                m10.reset()
                tip10_count = 0
            m10.pick_up_tip()
            tip10_count += 1
        else:
            if tip300_count == tip300_max:
                robot.pause('Replace 300ul tipracks before resuming')
                m300.reset()
                tip300_count = 0
            m300.pick_up_tip()
            tip300_count += 1

    # distribute nuclease-free water and beads to each sample
    m300.set_flow_rate(aspirate=100, dispense=250)
    pick_up(m300)
    m300.distribute(
        50,
        nuc_free_water,
        [s.top() for s in rxn_samples],
        new_tip='never'
    )
    for s in rxn_samples:
        if not m300.tip_attached:
            pick_up(m300)
        m300.transfer(100, beads, s, new_tip='never')
        m300.mix(5, 100, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    # incubate
    m300.delay(minutes=5)
    robot._driver.run_flag.wait()
    magdeck.engage(height=18)
    m300.delay(minutes=10)

    # remove supernatant
    for s in rxn_samples:
        pick_up(m300)
        m300.transfer(200, s, liquid_waste[0], new_tip='never')
        m300.drop_tip()

    # ethanol washes
    for wash in range(2):
        pick_up(m300)
        m300.transfer(
            200,
            etoh[wash],
            [s.top() for s in rxn_samples],
            new_tip='never',
            air_gap=10
            )

        # remove supernatant
        for s in rxn_samples:
            if not m300.tip_attached:
                pick_up(m300)
            m300.transfer(
                210, s, liquid_waste[wash], new_tip='never', air_gap=10)
            m300.drop_tip()

    # remove supernatant completely with P10 multi
    for s in rxn_samples:
        pick_up(m300)
        m300.transfer(50, s.bottom(), liquid_waste[0], new_tip='never')
        m300.drop_tip()

    # airdry
    m300.delay(minutes=7)
    robot._driver.run_flag.wait()
    magdeck.disengage()

    for s in rxn_samples:
        pick_up(m300)
        m300.transfer(52, nuc_free_water, s, new_tip='never')
        m300.mix(5, 40, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    magdeck.engage(height=18)
    robot.pause('Empy tips from the waste, and resume once the reaction \
solution has cleared.')

    # transfer to elution plate
    for s, d in zip(rxn_samples, elution_samples):
        pick_up(m300)
        m300.transfer(50, s, d, new_tip='never')
        m300.drop_tip()

    magdeck.disengage()
    robot.pause('Place elution plate on the magnetic deck.')

    # add beads and mix
    for s in rxn_samples:
        pick_up(m300)
        m300.transfer(50, beads, s, new_tip='never')
        m300.mix(5, 30, s)
        m300.blow_out(s.top())
        m300.drop_tip()

    m300.delay(minutes=5)
    robot._driver.run_flag.wait()
    magdeck.engage(height=18)
    m300.delay(minutes=5)

    # remove supernatant
    for s in rxn_samples:
        pick_up(m300)
        m300.transfer(110, s, liquid_waste[2], new_tip='never')
        m300.drop_tip()

    # ethanol washes
    for wash in range(2, 4):
        pick_up(m300)
        m300.transfer(
            200,
            etoh[wash],
            [s.top() for s in rxn_samples],
            new_tip='never',
            air_gap=10
        )

        # remove supernatant
        for s in rxn_samples:
            if not m300.tip_attached:
                pick_up(m300)
            m300.transfer(
                210, s, liquid_waste[wash], new_tip='never', air_gap=10)
            m300.drop_tip()

    # remove supernatant completely with P10 multi
    for s in rxn_samples:
        pick_up(m10)
        m10.transfer(7, s.bottom(), liquid_waste[0], new_tip='never')
        m10.drop_tip()

    # airdry
    robot.comment('Airdrying for 4 minutes.')
    m300.delay(minutes=4)
    robot._driver.run_flag.wait()
    magdeck.disengage()

    for s in rxn_samples:
        pick_up(m10)
        m10.transfer(12, nuc_free_water, s.top(-2), new_tip='never')
        m10.mix(5, 5, s)
        m10.blow_out(s.top())
        m10.drop_tip()

    magdeck.engage(height=18)
    m300.delay(minutes=1)
    robot._driver.run_flag.wait()
    robot.pause('Resume once the reaction solution has cleared. Place a fresh \
elution plate in slot 2.')

    # transfer to elution plate
    for s, d in zip(rxn_samples, elution_samples):
        pick_up(m10)
        m10.transfer(9.4, s, d, new_tip='never')
        m10.drop_tip()

    magdeck.disengage()
    robot.comment('Proceed with target enrichment. Alternatively, the samples \
can be stored at –20°C in a constant-temperature freezer for up to 3 days.')
