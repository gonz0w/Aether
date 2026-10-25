/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-channel/channel.h"
#include <sys/auxv.h>
#include <string.h>
static unsigned long input,output;
static _Thread_local volatile unsigned tls=53;
long bridge_read(unsigned char *p,unsigned long n){return channel_raw(0x24001,input,(uintptr_t)p,n);}
long bridge_write(const unsigned char *p,unsigned long n){return channel_raw(0x24002,output,(uintptr_t)p,n);}
void bridge_yield(void){channel_yield();}
_Noreturn void bridge_abort(void){channel_raw(0x1003c,123,0,0);for(;;){}}
extern int file_service(void);
int main(int argc,char **argv){
    if(tls!=53 || argc!=2 || strcmp(argv[0],"h") || strcmp(argv[1],"files"))return 124;
    input=getauxval(0xa001);output=getauxval(0xa002);
    if(!input || !output || input==output)return 126;
    int r=file_service();return r?r:17;
}
