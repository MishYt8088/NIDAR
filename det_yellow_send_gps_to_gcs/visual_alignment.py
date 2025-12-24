def compute_alignment_velocity(cx, cy, center_x, center_y, max_vel=0.2):
    """
    Returns vx, vy body-frame velocity commands (m/s)
    """
    error_x = cx - center_x
    error_y = cy - center_y

    # Normalize errors
    norm_x = error_x / center_x
    norm_y = error_y / center_y

    # Small proportional control
    vx = -norm_y * max_vel   # forward/back
    vy =  norm_x * max_vel   # left/right

    # Clamp velocities
    vx = max(-max_vel, min(max_vel, vx))
    vy = max(-max_vel, min(max_vel, vy))

    return vx, vy
