// CWrapper.cpp
#include "CWrapper.h"
#include "AbbrvE.h"
#include "AbbrStra.h"
#include "Ab3P.h"

extern "C" {

struct Ab3PWrapper {
    iret::Ab3P *ab3p;
};

Ab3PWrapper* create_ab3p() {
    Ab3PWrapper* ab3pWrapper = new Ab3PWrapper;
    ab3pWrapper->ab3p = new iret::Ab3P();
    return ab3pWrapper;
}

void destroy_ab3p(Ab3PWrapper* ab3pWrapper) {
    if (ab3pWrapper) {
        delete ab3pWrapper->ab3p;
        delete ab3pWrapper;
    }
}

void add_text(Ab3PWrapper* ab3pWrapper, const char* text) {
    if (ab3pWrapper) {
        ab3pWrapper->ab3p->add_text(text);
    }
}

void get_abbrs(Ab3PWrapper* ab3pWrapper, CAbbrOut* abbrs, int* abbrs_count) {
    if (ab3pWrapper) {
        std::vector<iret::AbbrOut> cppAbbrs;
        ab3pWrapper->ab3p->get_abbrs(cppAbbrs);

        *abbrs_count = cppAbbrs.size();
        if (abbrs != nullptr) {
            for (size_t i = 0; i < cppAbbrs.size(); ++i) {
                abbrs[i].sf = cppAbbrs[i].sf.c_str();
                abbrs[i].lf = cppAbbrs[i].lf.c_str();
                abbrs[i].strat = cppAbbrs[i].strat.c_str();
                abbrs[i].sf_offset = cppAbbrs[i].sf_offset;
                abbrs[i].lf_offset = cppAbbrs[i].lf_offset;
                abbrs[i].prec = cppAbbrs[i].prec;
            }
        }
    }
}

}
