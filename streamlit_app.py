import streamlit as st
from PIL import Image
import io
import numpy as np

st.title("Image to WebP Animation Converter")

# File uploader for multiple images
uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    # Display uploaded images
    st.write("Uploaded images:")
    cols = st.columns(len(uploaded_files))
    images = []
    
    # Find the maximum dimensions
    max_width = 0
    max_height = 0
    for file in uploaded_files:
        img = Image.open(file)
        max_width = max(max_width, img.width)
        max_height = max(max_height, img.height)
    
    # Open and resize images
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        # Create new image with max dimensions and paste original image centered
        new_img = Image.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
        x = (max_width - img.width) // 2
        y = (max_height - img.height) // 2
        new_img.paste(img, (x, y))
        cols[i].image(new_img, caption=f"Image {i+1}", use_container_width=True)
        images.append(new_img)
    
    # Delay slider
    delay = st.slider("Delay between frames (milliseconds)", 
                     min_value=100, 
                     max_value=2000, 
                     value=500,
                     step=100)

    # Quality slider
    quality = st.slider("Quality", 
                       min_value=1,
                       max_value=100,
                       value=80)
    
    # Number of transition frames slider
    transition_frames = st.slider("Number of transition frames",
                                min_value=0,
                                max_value=30,
                                value=0)
    
    if st.button("Create Animation"):
        if len(images) > 1:
            # Create animation with transitions
            final_images = []
            
            for i in range(len(images)):
                current_img = np.array(images[i])
                next_img = np.array(images[(i + 1) % len(images)])
                
                final_images.append(Image.fromarray(current_img))
                
                # Create transition frames only if transition_frames > 0
                if transition_frames > 0:
                    for j in range(transition_frames):
                        alpha = j / transition_frames
                        transition_frame = (1 - alpha) * current_img + alpha * next_img
                        transition_frame = transition_frame.astype(np.uint8)
                        final_images.append(Image.fromarray(transition_frame))
            
            # Create animation
            output = io.BytesIO()
            final_images[0].save(
                output,
                format='WebP',
                save_all=True,
                append_images=final_images[1:],
                duration=max(1, delay if transition_frames == 0 else delay // (transition_frames + 1)),
                loop=0,
                lossless=quality == 100,
                quality=min(100, quality) if quality < 100 else 100
            )
            
            # Create download button
            st.download_button(
                label="Download Animation",
                data=output.getvalue(),
                file_name="animation.webp",
                mime="image/webp"
            )
        else:
            st.error("Please upload at least 2 images to create an animation.")
else:
    st.info("Please upload some images to get started.")
