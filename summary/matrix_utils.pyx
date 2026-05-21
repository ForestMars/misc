# distutils: language = c++
# cython: boundscheck=False, wraparound=False, nonecheck=False, language_level=3

from libcpp.string cimport string

# Define the ANSI escape layouts as native Python text literals to ensure clean shell decoding
DIM = "\033[2m"
BRIGHT_CYAN = "\033[1;36m"
GREEN = "\033[92m"
RESET = "\033[0m"
DIVIDER = "──────────────────────────────────────────────────────────────────────"

def c_slice_document(str raw_text, int max_chars):
    """Component 1: Document data slicing using zero-allocation C++ buffers."""
    cdef string c_str = raw_text.encode('utf-8')
    if c_str.length() > <size_t>max_chars:
        return c_str.substr(0, max_chars).decode('utf-8')
    return raw_text

def c_build_system_instruction(str base_instruction, str style_nudge):
    """Component 2: Stateless instruction compiler."""
    return f"{base_instruction}\n\nStyle Alignment: {style_nudge}"

def c_render_dashboard(str output_text, 
                        str style_name, 
                        str format_name, 
                        float temperature, 
                        float top_p, 
                        float repetition_penalty, 
                        str inquiry_text):
    """Component 3: Pure presentation layer. 
    Accepts explicitly unpacked raw primitives—zero dictionary lookups.
    """
    cdef str template = (
        f"\n{DIM}[Matrix Engine: {style_name.upper()} ✕ {format_name.upper()}]\n"
        f"[Parameters: temp={temperature:.2f} | top_p={top_p:.2f} | rep_pen={repetition_penalty:.2f}]{RESET}\n"
        f"{DIM}❯ Lens Inquiry: {RESET}{BRIGHT_CYAN}{inquiry_text}{RESET}\n"
        f"{DIVIDER}\n"
        f"{GREEN}{output_text}{RESET}\n"
        f"{DIVIDER}\n"
    )
    print(template)
