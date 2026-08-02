from diffusers import StableDiffusionPipeline
import torch

# Model name
model_id = "runwayml/stable-diffusion-v1-5"

# Load the Stable Diffusion model (use float32 for CPU)
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float32
)

# Run on CPU
pipe = pipe.to("cpu")

# Text prompt
prompt = "Nice beach with on special day for friendship day"

# Generate image
image = pipe(prompt).images[0]

# Save the generated image in the same folder as app.py
image.save("generated_image2.png")

# Open the generated image automatically
image.show()

# Print confirmation message
print("Image generated successfully!")
print("Saved as generated_image2.png")