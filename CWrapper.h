// CWrapper.h
#ifdef __cplusplus
extern "C" {
#endif

struct CAbbrOut {
    const char *sf;
    const char *lf;
    const char *strat;
    int sf_offset;
    int lf_offset;
    double prec;
};

struct Ab3PWrapper;

Ab3PWrapper* create_ab3p();
void destroy_ab3p(Ab3PWrapper* ab3p);
void add_text(Ab3PWrapper* ab3p, const char* text);
void get_abbrs(Ab3PWrapper* ab3p, CAbbrOut* abbrs, int* abbrs_count);

#ifdef __cplusplus
}
#endif
