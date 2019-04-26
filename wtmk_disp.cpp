#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <cstdio>
#include <string>
#include <vector>
#include <chrono>

int main(int argc, char **argv) {
    int n_frames = argc - 1;
    int width, height;
    int frame, frame_save;

    std::vector<SDL_Surface*> surfaces;
    std::vector<SDL_Texture*> textures;
    decltype(std::chrono::steady_clock::now()) start;

    SDL_Window *window = nullptr;
    SDL_Renderer *renderer = nullptr;
    SDL_Event e;

    if (n_frames <= 0) {
        fprintf(stderr, "Please specify frames!");
        goto fail;
    }

    surfaces.reserve(n_frames);
    textures.reserve(n_frames);

    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "SDL could not initialize! SDL Error: %s\n", SDL_GetError());
        goto fail;
    }

    if ((IMG_Init(IMG_INIT_PNG) & IMG_INIT_PNG ) == 0) {
        fprintf(stderr, "SDL_image could not initialize! SDL_image Error: %s\n", SDL_GetError());
        goto fail;
    }

    width = height = -1;
    for (int i=1; i<=n_frames; i++) {
        SDL_Surface* s = IMG_Load(argv[i]);

        if (s == nullptr) {
            fprintf(stderr, "Surface could not be created! SDL Error: %s\n", SDL_GetError());
            goto fail;
        }

        surfaces.push_back(s);

        if (width < 0 || height < 0) {
            width = s->w;
            height = s->h;
        }

        if (s->w != width || s->h != height) {
            fprintf(stderr, "Image size must be the same!");
            goto fail;
        }
    }

    window = SDL_CreateWindow("Watermark", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, width, height, SDL_WINDOW_SHOWN);
    SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN_DESKTOP);
    if (window == nullptr) {
        fprintf(stderr, "Window could not be created! SDL Error: %s\n", SDL_GetError());
        goto fail;
    }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (renderer == nullptr) {
        fprintf(stderr, "Renderer could not be created! SDL Error: %s\n", SDL_GetError());
        return -1;
    }

    for (SDL_Surface *s: surfaces) {
        SDL_Texture *t = SDL_CreateTextureFromSurface(renderer, s);
        if (t == nullptr) {
            fprintf(stderr, "Texture could not be created! SDL Error: %s\n", SDL_GetError());
            return -1;
        }
        textures.push_back(t);
        SDL_FreeSurface(s);
    }
    surfaces.clear();

    frame = frame_save = 0;
    start = std::chrono::steady_clock::now();

    int log_w, log_h;
    SDL_GetRendererOutputSize(renderer, &log_w, &log_h);
    for (bool quit=false; !quit; frame++) {
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> diff = now - start;
        if (diff.count() >= 4.0) {
            double fps = (frame - frame_save) / diff.count();
            printf("FPS: %.2lf\n", fps);
            fflush(stdout);
            start = now;
            frame_save = frame;
        }

        while (SDL_PollEvent(&e))
            if (e.type == SDL_QUIT)
                quit = true;

        SDL_Rect dest = {
            .x = log_w / 2 - 270,
            .y = log_h / 2 - 270,
            .w = 540,
            .h = 540
        };

        //SDL_RenderCopy(renderer, textures[frame % n_frames], nullptr, nullptr);
        SDL_RenderCopy(renderer, textures[frame % n_frames], nullptr, &dest);
        SDL_RenderPresent(renderer);
    }

fail:
    for (SDL_Surface *s: surfaces)
        if (s) SDL_FreeSurface(s);
    for (SDL_Texture *t: textures)
        if (t) SDL_DestroyTexture(t);
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window) SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
