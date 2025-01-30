#version 130
uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform sampler2D near_geometry_color;
uniform sampler2D near_geometry_depth;
uniform vec2 camera_nearfar;
uniform float refractive_index;

in vec2 texcoord;
out vec4 fragColor;

const int NUM_SAMPLES = 7;
const float min_error = 1e-2; 
const int max_iterations = 5; 

void main() {
    float scene_depth = texture(depth_texture, texcoord).r;
    float near = camera_nearfar.x;
    float far = camera_nearfar.y;
    float z = (2.0 * near * far) / (far + near - (2.0 * scene_depth - 1.0) * (far - near));

    vec2 refracted_coords = texcoord;
    vec3 final_color = vec3(0.0);
    
    vec2 best_coords = refracted_coords;
    float min_depth_error = 1e6;

    //Multiple depth sampling along the refracted ray
    for (int j = 0; j < NUM_SAMPLES; ++j) {
        vec2 sample_coords = texcoord + j * (refracted_coords - texcoord) / float(NUM_SAMPLES);
        float sampled_depth = texture(near_geometry_depth, sample_coords).r;
        float sampled_z = (2.0 * near * far) / (far + near - (2.0 * sampled_depth - 1.0) * (far - near));

        float depth_error = abs(sampled_z - z);
        if (depth_error < min_depth_error) {
            min_depth_error = depth_error;
            best_coords = sample_coords;
        }
    }

    //Starting iteration from the best point
    refracted_coords = best_coords;
    for (int i = 0; i < max_iterations; ++i) {
        float new_depth = texture(near_geometry_depth, refracted_coords).r;
        float new_z = (2.0 * near * far) / (far + near - (2.0 * new_depth - 1.0) * (far - near));

        if (abs(new_z - z) < min_error) {
            final_color = texture(near_geometry_color, refracted_coords).rgb;
            break;
        }
        refracted_coords += vec2(0.01, 0.01) * (1.0 / refractive_index);
    }

    fragColor = vec4(final_color, 1.0);
}
