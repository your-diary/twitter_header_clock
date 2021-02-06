num_frame='29.97'
output_dir='./frames'

if [[ $# == 1 ]]; then
    mkdir -p "${output_dir}"
    ffmpeg -i "$1" -r "${num_frame}" "${output_dir}/%04d.png"
else
    echo "Usage: ./create_frames.sh <video file>"
fi

