# DAKboard Integration

DAKboard is the first supported display client for FrameFlow.

## Integration goal

FrameFlow should provide DAKboard with a stable image URL or feed that returns display-ready photos without relying on DAKboard's native cloud album rotation.

## Expected DAKboard usage

A user should be able to configure a DAKboard image block or custom block with a FrameFlow URL such as:

```text
https://frameflow.example.com/d/<display-token>/next.jpg
```

For local-only deployments, the URL may be on the home network. For remote family displays, the user will need a secure remote access approach, such as a reverse proxy, tunnel, or VPN. Native remote access guidance should be documented before recommending public exposure.

## Requirements

- Return a valid image response.
- Avoid redirect loops.
- Support cache behavior that does not cause DAKboard to show stale images forever.
- Keep tokenized display access separate from admin access.
- Select photos through the rotation engine, not by random file serving.
- Record display events when DAKboard requests a new image.

## Cache strategy

DAKboard and browsers may cache image URLs aggressively. FrameFlow should support cache-safe behavior by either:

- returning appropriate cache headers for `next.jpg`, or
- supporting a feed response with versioned asset URLs, or
- documenting a cache-busting query strategy.

The first implementation should test actual DAKboard behavior before finalizing endpoint semantics.

## Display-specific derivatives

DAKboard displays may have different resolutions and orientations. FrameFlow should be able to generate display-specific derivatives so each display receives appropriately sized images.

## Out of scope for the first DAKboard milestone

- full DAKboard account API integration
- managing DAKboard screens directly
- editing DAKboard layouts
- replacing DAKboard as a dashboard product
