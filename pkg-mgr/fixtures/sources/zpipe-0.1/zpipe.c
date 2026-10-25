/* Small zlib-stream filter for the pkg-mgr dependency fixture. */
#include <stdio.h>
#include <string.h>
#include <zlib.h>

static int transform(int compressing)
{
    unsigned char input[16384], output[16384];
    z_stream stream = {0};
    int result = 1, ended = 0;
    int status = compressing ? deflateInit(&stream, Z_DEFAULT_COMPRESSION)
                             : inflateInit(&stream);
    if (status != Z_OK) return 1;
    while (!ended) {
        size_t count = fread(input, 1, sizeof input, stdin);
        int flush = feof(stdin) ? Z_FINISH : Z_NO_FLUSH;
        if (ferror(stdin)) goto done;
        if (!compressing && count == 0) goto done; /* truncated stream */
        stream.next_in = input;
        stream.avail_in = (uInt)count;
        do {
            size_t produced;
            stream.next_out = output;
            stream.avail_out = sizeof output;
            status = compressing ? deflate(&stream, flush)
                                 : inflate(&stream, Z_NO_FLUSH);
            if (status == Z_BUF_ERROR && stream.avail_in == 0 &&
                (!compressing || flush != Z_FINISH)) break;
            if (status != Z_OK && status != Z_STREAM_END) goto done;
            produced = sizeof output - stream.avail_out;
            if (fwrite(output, 1, produced, stdout) != produced) goto done;
            ended = status == Z_STREAM_END;
        } while (!ended && (stream.avail_in || stream.avail_out == 0 ||
                            (compressing && flush == Z_FINISH)));
        if (ended && !compressing) {
            if (stream.avail_in || getchar() != EOF || ferror(stdin)) goto done;
        }
    }
    if (fflush(stdout) != 0) goto done;
    result = 0;
done:
    if (compressing) deflateEnd(&stream); else inflateEnd(&stream);
    return result;
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        printf("zpipe 0.1; zlib headers=%s linked=%s\n", ZLIB_VERSION, zlibVersion());
        return strcmp(ZLIB_VERSION, zlibVersion()) != 0;
    }
    if (argc != 2 || (strcmp(argv[1], "c") && strcmp(argv[1], "d"))) {
        fprintf(stderr, "usage: zpipe c|d < input > output\n");
        return 64;
    }
    if (transform(strcmp(argv[1], "c") == 0)) {
        fprintf(stderr, "zpipe: invalid/truncated stream or I/O failure\n");
        return 1;
    }
    return 0;
}
