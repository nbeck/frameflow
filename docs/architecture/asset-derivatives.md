# Asset Derivatives

Generated derivatives are display-ready versions of immutable originals.

## Why derivatives exist

Original photos may be too large, incorrectly oriented, inefficient to serve, or poorly matched to a display. Derivatives let FrameFlow optimize display delivery without modifying originals.

## Derivative types

Initial derivative types:

- thumbnail
- preview
- display image

Future derivative types:

- blurred low-resolution preview
- cropped display image
- letterboxed display image
- video poster frame

## Recipe model

A derivative should be tied to a recipe. A recipe describes the transformation inputs, such as:

- target width
- target height
- output format
- fit mode
- quality
- background strategy
- orientation behavior

When a recipe changes, existing derivatives created from the old recipe should be invalidated and regenerated.

## Rebuildability

Generated derivatives should be disposable. If the `generated/` directory is deleted, FrameFlow should be able to rebuild needed derivatives from originals and database records.

## Validation

A generated derivative is valid only if:

- the source original exists
- the recipe version matches
- the generated file exists
- the generated file can be decoded
- dimensions match the recipe expectation or documented fit behavior
