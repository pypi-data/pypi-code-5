# SDL2's SDL_image bindings for pysdl2-cffi.

import sys
import cffi
import os.path

import _sdl.cdefs
from _sdl.internal import guard

__missing_functions = []

def lookup(name):
    if hasattr(_LIB, name):
        return getattr(_LIB, name)
    __missing_functions.append(name)
    return None

ffi = cffi.FFI()
ffi.include(_sdl.cdefs.ffi)

# SDL_image uses SDL_SetError / SDL_GetError for error reporting.

ffi.cdef("""

extern const SDL_version * IMG_Linked_Version(void);

typedef enum
{
    IMG_INIT_JPG = 0x00000001,
    IMG_INIT_PNG = 0x00000002,
    IMG_INIT_TIF = 0x00000004,
    IMG_INIT_WEBP = 0x00000008
} IMG_InitFlags;

extern int IMG_Init(int flags);

extern void IMG_Quit(void);

extern SDL_Surface * IMG_LoadTyped_RW(SDL_RWops *src, int freesrc, const char *type);

extern SDL_Surface * IMG_Load(const char *file);
extern SDL_Surface * IMG_Load_RW(SDL_RWops *src, int freesrc);

extern SDL_Texture * IMG_LoadTexture(SDL_Renderer *renderer, const char *file);
extern SDL_Texture * IMG_LoadTexture_RW(SDL_Renderer *renderer, SDL_RWops *src, int freesrc);
extern SDL_Texture * IMG_LoadTextureTyped_RW(SDL_Renderer *renderer, SDL_RWops *src, int freesrc, const char *type);

extern int IMG_isICO(SDL_RWops *src);
extern int IMG_isCUR(SDL_RWops *src);
extern int IMG_isBMP(SDL_RWops *src);
extern int IMG_isGIF(SDL_RWops *src);
extern int IMG_isJPG(SDL_RWops *src);
extern int IMG_isLBM(SDL_RWops *src);
extern int IMG_isPCX(SDL_RWops *src);
extern int IMG_isPNG(SDL_RWops *src);
extern int IMG_isPNM(SDL_RWops *src);
extern int IMG_isTIF(SDL_RWops *src);
extern int IMG_isXCF(SDL_RWops *src);
extern int IMG_isXPM(SDL_RWops *src);
extern int IMG_isXV(SDL_RWops *src);
extern int IMG_isWEBP(SDL_RWops *src);

extern SDL_Surface * IMG_LoadICO_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadCUR_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadBMP_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadGIF_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadJPG_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadLBM_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadPCX_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadPNG_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadPNM_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadTGA_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadTIF_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadXCF_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadXPM_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadXV_RW(SDL_RWops *src);
extern SDL_Surface * IMG_LoadWEBP_RW(SDL_RWops *src);

extern SDL_Surface * IMG_ReadXPMFromArray(char **xpm);

extern int IMG_SavePNG(SDL_Surface *surface, const char *file);
extern int IMG_SavePNG_RW(SDL_Surface *surface, SDL_RWops *dst, int freedst);
""")

if sys.platform == 'darwin':
    _LIB = ffi.dlopen('SDL2_image')
else:
    _LIB = ffi.dlopen('libSDL2_image.so')

IMG_INIT_JPG = lookup('IMG_INIT_JPG')
IMG_INIT_PNG = lookup('IMG_INIT_PNG')
IMG_INIT_TIF = lookup('IMG_INIT_TIF')
IMG_INIT_WEBP = lookup('IMG_INIT_WEBP')

IMG_Init = guard(lookup("IMG_Init"))
IMG_InitJPG = guard(lookup("IMG_InitJPG"))
IMG_InitPNG = guard(lookup("IMG_InitPNG"))
IMG_InitTIF = guard(lookup("IMG_InitTIF"))
IMG_InitWEBP = guard(lookup("IMG_InitWEBP"))
IMG_isBMP = guard(lookup("IMG_isBMP"))
IMG_isCUR = guard(lookup("IMG_isCUR"))
IMG_isGIF = guard(lookup("IMG_isGIF"))
IMG_isICO = guard(lookup("IMG_isICO"))
IMG_isJPG = guard(lookup("IMG_isJPG"))
IMG_isLBM = guard(lookup("IMG_isLBM"))
IMG_isPCX = guard(lookup("IMG_isPCX"))
IMG_isPNG = guard(lookup("IMG_isPNG"))
IMG_isPNM = guard(lookup("IMG_isPNM"))
IMG_isTIF = guard(lookup("IMG_isTIF"))
IMG_isWEBP = guard(lookup("IMG_isWEBP"))
IMG_isXCF = guard(lookup("IMG_isXCF"))
IMG_isXPM = guard(lookup("IMG_isXPM"))
IMG_isXV = guard(lookup("IMG_isXV"))
IMG_Linked_Version = guard(lookup("IMG_Linked_Version"))
IMG_Load = guard(lookup("IMG_Load"))
IMG_LoadBMP_RW = guard(lookup("IMG_LoadBMP_RW"))
IMG_LoadCUR_RW = guard(lookup("IMG_LoadCUR_RW"))
IMG_LoadGIF_RW = guard(lookup("IMG_LoadGIF_RW"))
IMG_LoadICO_RW = guard(lookup("IMG_LoadICO_RW"))
IMG_LoadJPG_RW = guard(lookup("IMG_LoadJPG_RW"))
IMG_LoadLBM_RW = guard(lookup("IMG_LoadLBM_RW"))
IMG_LoadPCX_RW = guard(lookup("IMG_LoadPCX_RW"))
IMG_LoadPNG_RW = guard(lookup("IMG_LoadPNG_RW"))
IMG_LoadPNM_RW = guard(lookup("IMG_LoadPNM_RW"))
IMG_Load_RW = guard(lookup("IMG_Load_RW"))
IMG_LoadTexture = guard(lookup("IMG_LoadTexture"))
IMG_LoadTexture_RW = guard(lookup("IMG_LoadTexture_RW"))
IMG_LoadTextureTyped_RW = guard(lookup("IMG_LoadTextureTyped_RW"))
IMG_LoadTGA_RW = guard(lookup("IMG_LoadTGA_RW"))
IMG_LoadTIF_RW = guard(lookup("IMG_LoadTIF_RW"))
IMG_LoadTyped_RW = guard(lookup("IMG_LoadTyped_RW"))
IMG_LoadWEBP_RW = guard(lookup("IMG_LoadWEBP_RW"))
IMG_LoadXCF_RW = guard(lookup("IMG_LoadXCF_RW"))
IMG_LoadXPM_RW = guard(lookup("IMG_LoadXPM_RW"))
IMG_LoadXV_RW = guard(lookup("IMG_LoadXV_RW"))
IMG_Quit = guard(lookup("IMG_Quit"))
IMG_QuitJPG = guard(lookup("IMG_QuitJPG"))
IMG_QuitPNG = guard(lookup("IMG_QuitPNG"))
IMG_QuitTIF = guard(lookup("IMG_QuitTIF"))
IMG_QuitWEBP = guard(lookup("IMG_QuitWEBP"))

IMG_GetError = _sdl.internal.SDL_GetError
IMG_SetError = _sdl.internal.SDL_SetError
