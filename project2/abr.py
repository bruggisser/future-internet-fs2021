from enum import Enum
import math


class CALLBACK_EVENT(Enum):
    INIT = 0
    DOWNLOAD_COMPLETED = 1
    TIMEOUT = 2
    REBUFFERING = 3


def abr(
        typ,
        current_time,
        playback_time,
        playback_chunk,
        current_chunk,
        current_chunk_quality,
        current_chunk_download,
        video
):
    """
        typ - type of event
            INIT - initial call at time 0
            DOWNLOAD_COMPLETED - a chunk has been downloaded
            TIMEOUT - timeout has happend
            REBUFFERING - rebuffering started

        current_time - time from the beginning of the simulation in seconds

        playback_time - how much of the video has been shown (in seconds)
        playback_chunk - the chunk that is playing right now
        current_chunk - the chunk number that is downloading right now (or has been just finished)
        current_chunk_quality - the quality of the current_chunk
        current_chunk_download - how much of current_chunk has been downloaded (in bytes)
        video - contains 6 video arrays (one per quality level) - Each subarray contain the size of each chunk in the video

        Returns
            quality_to_download_now, chunk_to_download_now, timeout

        ABR function returns the next chunk that should be downloaded
           * quality_to_download_now - quality of the next chunk from 0 to 5
           * chunk_to_download_now   - chunk number of the chunk that should be downloaded
                                     - next_chunk cannot be in the past, if the player plays chunk 10, chunk 9 shouldn't be downloaded
                                     - if you set next_chunk to -1, no chunk will be downloaded
                                     - if the previou download hasn't been completed (e.g. in case of rebuffering) you can change the chunk
                                       that is currently downloading. For instance, you started downloading a high quality chunk, but
                                       rebuffering happened and now you would like to lower the quality. In that case, return the same chunk
                                       number, but different quality.
           * timeout    - set a timer that will trigger the abr function again
                        - timeout is in absolute time, usually set it as current_time+X (where min X is 200ms)
                        - timeout 0 means no timeout
    """

    # initial
    if typ == CALLBACK_EVENT.INIT:
        abr.DOWNLOAD_START = current_time
        abr.ESTIMATED_CAPACITY = 1200
        abr.BUFFER_SIZE = 0
        abr.INITIAL = True
        abr.MAX_STALL = 5
        abr.DOWNLOAD_DURATION = 0
        abr.QUALITIES = [300, 750, 1200, 1850, 2850, 4300]
        abr.THRESHOLDS = [9, 11.5, 14, 16, 18]  # arbitrarily chosen thresholds
        return 0, 0, 0.0

    elif typ == CALLBACK_EVENT.DOWNLOAD_COMPLETED:
        abr.DOWNLOAD_END = current_time
        abr.ESTIMATED_CAPACITY = 4 * (
                0.9 * (1 / 4) * abr.ESTIMATED_CAPACITY + 0.1 * current_chunk_download / (
                abr.DOWNLOAD_END - abr.DOWNLOAD_START))  # Kbits/s

        buffer_size = current_chunk - playback_chunk
        buffer_size = buffer_size * 4 - (playback_time % 4)  #  to get buffer fill level in seconds
        abr.BUFFER_SIZE = buffer_size
        abr.DOWNLOAD_DURATION = (abr.DOWNLOAD_END - abr.DOWNLOAD_START)

        abr.DOWNLOAD_START = current_time
        if len(video[0]) - 1 == current_chunk:
            return 0, -1, 0
        if buffer_size < 1:
            return 0, current_chunk + 1, 0

        num_segments = math.ceil(min(buffer_size / 4, len(video[0]) - current_chunk - 1) / 4)

        abr.DOWNLOAD_START = current_time
        if len(video[0]) - 1 == current_chunk:
            return 0, -1, 0
        if buffer_size < 1:  #  arbritrarily chosen thresholds
            return 0, current_chunk + 1, 0

        abr.INITIAL = 0 < current_chunk < 5
        for i in range(1, 6):
            q = 6 - i
            download_size = 0.5 * video[0][0]  # find size of video to download with quality q, add some overhead
            if buffer_size > abr.THRESHOLDS[q - 1] or abr.INITIAL:
                for j in range(current_chunk, current_chunk + num_segments + 1):
                    download_size = download_size + video[q][j]
                if download_size / (
                        4 * num_segments) < abr.ESTIMATED_CAPACITY:  # 4 * num_segments = buffersize in s => kb/s
                    return max(current_chunk_quality, q), current_chunk + 1, 0

        if abr.DOWNLOAD_DURATION > 1.05 * abr.BUFFER_SIZE:
            return max(current_chunk_quality - 1, 0), current_chunk + 1, 0
        else:
            return current_chunk_quality, current_chunk + 1, 0

    if typ == CALLBACK_EVENT.REBUFFERING:
        abr.DOWNLOAD_START = current_time
        return 0, current_chunk, 0

    # unreachable code
    abr.DOWNLOAD_START = current_time
    return current_chunk_quality, current_chunk, 0
