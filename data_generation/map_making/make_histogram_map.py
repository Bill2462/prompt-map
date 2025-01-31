import cv2
import argparse
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)

    parser.add_argument("--hist_n_bins", type=int, default=2000)
    parser.add_argument("--rescale_factor", type=float, default=4.0)
    parser.add_argument("--gaussian_blur_kernel_size", type=int, default=5)
    parser.add_argument("--clip_threshold", type=int, default=60)

    return parser.parse_args()

def main():
    args = get_args()

    data = np.load(args.input)
    
    # Rescale points into <0, 1> range
    data = data - np.min(data, axis=0)
    data = data / np.max(data, axis=0)

    hist, _, _ = np.histogram2d(data[:, 0], data[:, 1], bins=args.hist_n_bins)
    hist = np.clip(hist, 0, args.clip_threshold)

    hist = hist / np.max(hist) * 255
    hist = hist.astype(np.uint8)

    hist = cv2.resize(hist,
                      (int(hist.shape[1] * args.rescale_factor),
                       int(hist.shape[0] * args.rescale_factor)),
                      interpolation=cv2.INTER_LINEAR)
    
    hist = cv2.GaussianBlur(hist, (args.gaussian_blur_kernel_size,
                                   args.gaussian_blur_kernel_size), 0)
    
    hist = cv2.cvtColor(hist, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(args.output, hist)

if __name__ == "__main__":
    main()
