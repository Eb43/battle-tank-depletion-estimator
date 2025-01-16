import base64

# File paths
input_file = r"c:\temporary_downloads\1.png"  # Path to the input image
output_file = r"c:\temporary_downloads\trum1_base64.txt"  # Path to the output file

# Read and encode the image, then write the Base64 string to a file
with open(input_file, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

with open(output_file, "w") as file:
    file.write(encoded_string)

print(f"Base64-encoded string written to {output_file}")

# <img src="data:image/jpeg;base64,BASE64_STRING" alt="Embedded Image">
# BASE64_STRING to be replaced
