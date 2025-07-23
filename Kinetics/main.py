import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import time

class TricycleModel:
    """Front-wheel drive tricycle chassis kinematic model - Fixed view version"""
    
    def __init__(self, 
                 x0=0.0, y0=0.0, theta0=0.0,  # Initial position and angle
                 d=1.0,                       # Wheelbase
                 gamma_max=np.pi/4,           # Maximum steering angle
                 omega_max=np.pi/2,           # Maximum steering angular velocity
                 a_omega=np.pi,               # Steering angular acceleration
                 v_max=2.0,                   # Maximum linear velocity
                 a_v=1.0,                     # Linear acceleration
                 view_range=15):              # Fixed view range
        
        # Vehicle state [x, y, theta]
        self.x = x0
        self.y = y0
        self.theta = theta0
        
        # Kinematic parameters
        self.d = d                  # Wheelbase
        self.gamma_max = gamma_max  # Maximum steering angle
        self.omega_max = omega_max  # Maximum steering angular velocity
        self.a_omega = a_omega      # Steering angular acceleration
        self.v_max = v_max          # Maximum linear velocity
        self.a_v = a_v              # Linear acceleration
        self.view_range = view_range  # Fixed view range
        
        # Control states
        self.v_f = 0.0              # Current front wheel linear velocity
        self.gamma = 0.0            # Current front wheel steering angle
        self.omega = 0.0            # Current steering angular velocity
        
        # Time related
        self.last_time = time.time()
        
        # Visualization settings
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.fig.subplots_adjust(bottom=0.3)  # Leave space for controls
        
        # Trail related
        self.trail, = self.ax.plot([], [], 'r-', alpha=0.6, linewidth=1.5)  # Trail line
        self.trail_points = []  # Store trail points
        self.max_trail_points = 5000  # Increased for fixed view
        
        # Vehicle components
        self.body_patch = None
        self.front_wheel = None
        self.rear_wheel_left = None
        self.rear_wheel_right = None
        self.wheel_direction = None
        self.heading_indicator = None
        
        # Initialize visualization
        self._init_visualization()
        
    def _init_visualization(self):
        """Initialize visualization interface with fixed view"""
        # Set up fixed coordinate axes
        view = self.view_range
        self.ax.set_xlim(-view, view)
        self.ax.set_ylim(-view, view)
        self.ax.set_aspect('equal')
        self.ax.set_title('Front-Wheel Drive Tricycle Kinematic Model', fontsize=14)
        self.ax.set_xlabel('X Position (m)', fontsize=12)
        self.ax.set_ylabel('Y Position (m)', fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Draw origin marker
        self.ax.plot(0, 0, 'ko', markersize=5)
        self.ax.text(0.1, 0.1, 'Origin', fontsize=9)
        
        # Draw vehicle body
        self.body_patch = patches.Rectangle((-0.6, -0.4), 1.2, 0.8, 
                                           fc='#3498db', ec='black', linewidth=1.5)
        self.ax.add_patch(self.body_patch)
        
        # Draw rear wheels
        rear_wheel_offset = 0.35
        self.rear_wheel_left = patches.Ellipse((-0.5, -rear_wheel_offset), 0.3, 0.2, 
                                              fc='#2c3e50', ec='white', linewidth=0.5)
        self.rear_wheel_right = patches.Ellipse((-0.5, rear_wheel_offset), 0.3, 0.2, 
                                               fc='#2c3e50', ec='white', linewidth=0.5)
        self.ax.add_patch(self.rear_wheel_left)
        self.ax.add_patch(self.rear_wheel_right)
        
        # Draw front wheel
        self.front_wheel = patches.Ellipse((0.5, 0), 0.35, 0.25, 
                                          fc='#2c3e50', ec='white', linewidth=0.5)
        self.ax.add_patch(self.front_wheel)
        
        # Add state text
        self.state_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                      verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                                      fontsize=10)
        
        # Add control sliders
        ax_vf = self.fig.add_axes([0.2, 0.22, 0.65, 0.03])
        ax_gamma = self.fig.add_axes([0.2, 0.17, 0.65, 0.03])
        
        self.slider_vf = Slider(ax_vf, 'Front Wheel Speed (m/s)', -self.v_max, self.v_max, valinit=0, 
                               color='#3498db')
        self.slider_gamma = Slider(ax_gamma, 'Steering Angle (rad)', -self.gamma_max, self.gamma_max, valinit=0,
                                  color='#e74c3c')
        
        # Add reset button
        reset_ax = self.fig.add_axes([0.8, 0.12, 0.1, 0.04])
        self.reset_button = Button(reset_ax, 'Reset', color='#2ecc71', hovercolor='#27ae60')
        self.reset_button.on_clicked(self.reset_simulation)
        
        # Slider event handling
        self.slider_vf.on_changed(self.set_target_vf)
        self.slider_gamma.on_changed(self.set_target_gamma)
        
        # Target control values
        self.target_vf = 0.0
        self.target_gamma = 0.0
        
    def reset_simulation(self, event):
        """Reset the simulation"""
        # Reset state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v_f = 0.0
        self.gamma = 0.0
        self.omega = 0.0
        
        # Reset sliders
        self.slider_vf.reset()
        self.slider_gamma.reset()
        
        # Clear trail
        self.trail_points = []
        self.trail.set_data([], [])
        
        # Reset time
        self.last_time = time.time()
        
        # Clear direction indicators
        if self.wheel_direction is not None:
            self.wheel_direction.remove()
            self.wheel_direction = None
        if self.heading_indicator is not None:
            self.heading_indicator.remove()
            self.heading_indicator = None
        
    def set_target_vf(self, val):
        """Set target linear velocity"""
        self.target_vf = val
        
    def set_target_gamma(self, val):
        """Set target steering angle"""
        self.target_gamma = val
        
    def update_control(self, dt):
        """Update control values with kinematic constraints"""
        # Update linear velocity
        vf_error = self.target_vf - self.v_f
        max_delta_v = self.a_v * dt
        
        if abs(vf_error) <= max_delta_v:
            self.v_f = self.target_vf
        else:
            self.v_f += max_delta_v * np.sign(vf_error)
        
        self.v_f = np.clip(self.v_f, -self.v_max, self.v_max)
        
        # Update steering angle
        gamma_error = self.target_gamma - self.gamma
        max_delta_omega = self.a_omega * dt
        desired_omega = gamma_error / dt if dt > 0 else 0
        
        if abs(desired_omega - self.omega) <= max_delta_omega:
            self.omega = desired_omega
        else:
            self.omega += max_delta_omega * np.sign(desired_omega - self.omega)
        
        self.omega = np.clip(self.omega, -self.omega_max, self.omega_max)
        self.gamma += self.omega * dt
        self.gamma = np.clip(self.gamma, -self.gamma_max, self.gamma_max)
    
    def update_state(self, dt=None):
        """Update vehicle state based on kinematic model"""
        if dt is None:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
        
        if dt <= 0:
            return
        
        self.update_control(dt)
        
        # Update state according to kinematic model
        self.x += self.v_f * np.cos(self.gamma) * np.cos(self.theta) * dt
        self.y += self.v_f * np.cos(self.gamma) * np.sin(self.theta) * dt
        self.theta += (self.v_f * np.sin(self.gamma) / self.d) * dt
        
        # Keep angle within [-π, π] range
        self.theta = (self.theta + np.pi) % (2 * np.pi) - np.pi
        
        # Record trail points
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > self.max_trail_points:
            self.trail_points.pop(0)
    
    def update_visualization(self, frame):
        """Update visualization display with fixed view"""
        self.update_state()
        
        cos_theta = np.cos(self.theta)
        sin_theta = np.sin(self.theta)
        
        # Update vehicle body
        self.body_patch.set_xy((self.x - 0.6*cos_theta + 0.4*sin_theta, 
                               self.y - 0.6*sin_theta - 0.4*cos_theta))
        self.body_patch.set_angle(np.rad2deg(self.theta))
        
        # Update rear wheels
        rear_offset_x = -0.5 * cos_theta
        rear_offset_y = -0.5 * sin_theta
        
        rear_left_x = self.x + rear_offset_x - 0.35 * sin_theta
        rear_left_y = self.y + rear_offset_y + 0.35 * cos_theta
        self.rear_wheel_left.set_center((rear_left_x, rear_left_y))
        self.rear_wheel_left.set_angle(np.rad2deg(self.theta))
        
        rear_right_x = self.x + rear_offset_x + 0.35 * sin_theta
        rear_right_y = self.y + rear_offset_y - 0.35 * cos_theta
        self.rear_wheel_right.set_center((rear_right_x, rear_right_y))
        self.rear_wheel_right.set_angle(np.rad2deg(self.theta))
        
        # Update front wheel
        front_offset_x = 0.5 * cos_theta
        front_offset_y = 0.5 * sin_theta
        front_x = self.x + front_offset_x
        front_y = self.y + front_offset_y
        self.front_wheel.set_center((front_x, front_y))
        self.front_wheel.set_angle(np.rad2deg(self.theta + self.gamma))
        
        # Update front wheel direction indicator
        if self.wheel_direction is not None:
            self.wheel_direction.remove()
        wheel_dir_length = 0.5
        wheel_dir_x = front_x + wheel_dir_length * np.cos(self.theta + self.gamma)
        wheel_dir_y = front_y + wheel_dir_length * np.sin(self.theta + self.gamma)
        self.wheel_direction, = self.ax.plot([front_x, wheel_dir_x], [front_y, wheel_dir_y], 
                                            'r-', linewidth=2.5, alpha=0.8)
        
        # Update vehicle heading indicator
        if self.heading_indicator is not None:
            self.heading_indicator.remove()
        heading_length = 0.8
        heading_x = self.x + heading_length * np.cos(self.theta)
        heading_y = self.y + heading_length * np.sin(self.theta)
        self.heading_indicator, = self.ax.plot([self.x, heading_x], [self.y, heading_y], 
                                              'g-', linewidth=2, alpha=0.8)
        
        # Update trail
        if self.trail_points:
            xs, ys = zip(*self.trail_points)
            self.trail.set_data(xs, ys)
        
        # Update state text
        state_text = (f'Position: (x={self.x:.2f}, y={self.y:.2f}) m\n'
                     f'Heading angle: θ={np.rad2deg(self.theta):.1f}°\n'
                     f'Front wheel speed: v_f={self.v_f:.2f} m/s\n'
                     f'Steering angle: γ={np.rad2deg(self.gamma):.1f}°')
        self.state_text.set_text(state_text)
        
        # 移除了自动调整坐标轴范围的代码，保持视角固定
        
        return (self.body_patch, self.front_wheel, self.rear_wheel_left, 
                self.rear_wheel_right, self.trail, self.state_text, 
                self.wheel_direction, self.heading_indicator)
    
    def run_simulation(self):
        """Run simulation and display visualization"""
        ani = FuncAnimation(
            self.fig, 
            self.update_visualization, 
            interval=50, 
            blit=True,
            cache_frame_data=False,
            save_count=1000
        )
        plt.show()

if __name__ == "__main__":
    # Create tricycle model instance with fixed view range of 20 meters
    tricycle = TricycleModel(
        x0=0.0, y0=0.0, theta0=0.0,
        d=1.0,
        gamma_max=np.pi/3,    # 60 degrees
        omega_max=np.pi/2,    # 90 degrees/sec
        a_omega=np.pi,        # 180 degrees/sec²
        v_max=2.0,            # 2m/s
        a_v=1.0,              # 1m/s²
        view_range=20         # Fixed view range from -20 to 20 meters
    )
    
    # Run simulation
    tricycle.run_simulation()
    