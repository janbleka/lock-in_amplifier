from record import record
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Record audio from microphone to WAV file.')
    parser.add_argument('--output_file_name', required=True, help='Output file name. E.g. "output.wav".')
    parser.add_argument('--record_seconds', type=int, required=True, help='How many seconds to record. E.g. "3".')
    args = parser.parse_args()
    record(args.output_file_name, args.record_seconds)
