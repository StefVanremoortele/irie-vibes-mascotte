# Vision: Irie Vibes dancing mascot

Irie Vibes is a dub and reggae festival. We are experimenting with a character that can bring the festival's rhythm and personality onto its website: a friendly woofer mascot that grooves with the music, responds to visitors, and feels at home beside event information rather than distracting from it.

## What we want to create

- A recognizable mascot that keeps its visual identity across Blender renders and the live website.
- Dance that feels grounded and musical: feet carry weight, hips and torso follow the groove, and arms add personality. Dub's relaxed half-time feel should guide motion more than constant, frantic movement.
- A poseable rig that supports more than one loop: idle vibing, a few expressive dance clips, greetings, and occasional special moments.
- A lightweight Three.js experience that plays smoothly on desktop and mobile, with sound controlled by the visitor and a useful still or fallback when 3D is unavailable.
- A repeatable Blender-to-GLB pipeline so we can improve the character and choreography without rebuilding the web integration by hand.

## Where we are now

The original woofer model is imported and rigged in Blender. The current Open Mind experiment has an eight-beat dance loop with planted feet, small steps, torso lean, and arm motion. A Three.js page loads the GLB and aligns that loop to an MP3's playback time. Earlier 70 BPM and poseable versions remain available for comparison and further animation work.

## Next experiments

1. Review the dance in motion with festival collaborators and refine its character, balance, and silhouette from multiple angles.
2. Author distinct clips such as a welcoming idle, toprock, a playful freeze, and a bass-drop reaction. Give each clip clean transitions and loop points.
3. Decide how the website should use the mascot: where it appears, when it dances, when it rests, and how visitors start or stop sound.
4. Optimize the exported model and test loading, frame rate, accessibility, and reduced-motion behavior on mobile devices.
5. Connect dance changes to the music experience only where it improves the page; keep the mascot understandable and enjoyable without audio.

This is an exploration, not a finished festival feature. The immediate goal is to learn what animation and interaction make Irie Vibes feel present on the web, then turn the strongest experiment into a dependable website component.
