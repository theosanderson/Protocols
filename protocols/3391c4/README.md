# Cell Culture Cherrypick

### Author
[Opentrons](https://opentrons.com/)

## Categories
* Cell Culture
	* Assay

## Description
This protocol performs a cell culture cherrypicking assay from an input string of comma-separated values. The input string for the parameter 'cherrypick wells separated by comma' denotes the wells to be selected from each source plate to the destination plate; the input should be formatted as in the following example:

  `B6, C1, C4, D5, E7, F8`

In this case, wells B6, C1, C4, D5, E7, and F8 of the first source plate will be transferred to wells A1-F1, respectively of the destination plate. Then wells B6, C1, C4, D5, E7, and F8 of the second source plate will be transferred to wells G1-D2 of the destination plate, etc. A new tip is used for each transfer.

---
![Materials Needed](https://s3.amazonaws.com/opentrons-protocol-library-website/custom-README-images/001-General+Headings/materials.png)

* [Corning 96-well clear flat-bottom plates 360ul #351172](https://ecatalog.corning.com/life-sciences/b2c/US/en/Microplates/Assay-Microplates/96-Well-Microplates/Falcon%C2%AE-96-well-Polystyrene-Microplates/p/351172)
* [Opentrons P300 single-channel electronic pipette](https://shop.opentrons.com/collections/ot-2-pipettes/products/single-channel-electronic-pipette?variant=5984549109789)
* [Opentrons 300ul pipette tips](https://shop.opentrons.com/collections/opentrons-tips/products/opentrons-300ul-tips)

### Robot
* [OT-2](https://opentrons.com/ot-2)

## Process
1. Input the mount side for your P300 single-channel pipette, the volume to cherrypick (in ul), the comma-separated cherrypick wells, and the number of source plates to cherrypick from, and the tipracks start well.
2. Download your protocol.
3. Upload your protocol into the [OT App](https://opentrons.com/ot-app).
4. Set up your deck according to the deck map.
5. Calibrate your labware, tiprack and pipette using the OT App. For calibration tips, check out our [support articles](https://support.opentrons.com/en/collections/1559720-guide-for-getting-started-with-the-ot-2).
6. Hit "Run".

### Additional Notes
If you have any questions about this protocol, please contact the Protocol Development Team by filling out the [Troubleshooting Survey](https://protocol-troubleshooting.paperform.co/).

###### Internal
3391c4
