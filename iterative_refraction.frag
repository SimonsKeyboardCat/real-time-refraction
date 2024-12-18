
#version 130
uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform vec2 camera_nearfar;
uniform float refractive_index;
in vec2 texcoord;
out vec4 fragColor;
void main() {
    float scene_depth = texture(depth_texture, texcoord).r;
    float near = camera_nearfar.x;
    float far = camera_nearfar.y;
    float z = (2.0 * near * far) / (far + near - (2.0 * scene_depth - 1.0) * (far - near));
    vec2 refracted_coords = texcoord;
    for (int i = 0; i < 5; ++i) {
        float new_depth = texture(depth_texture, refracted_coords).r;
        float new_z = (2.0 * near * far) / (far + near - (2.0 * new_depth - 1.0) * (far - near));
        if (abs(new_z - z) < 0.01) break;
        refracted_coords += vec2(0.01, 0.01) * (1.0 / refractive_index);
    }
    vec4 color = texture(color_texture, refracted_coords);
    fragColor = color;
}
