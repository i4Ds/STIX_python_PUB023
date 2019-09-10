#include <stdint.h>
#include <iostream>
#include <string>    
using namespace std; 
uint8_t CompressionAlgorithms_compressS0(uint32_t in_val,uint8_t K=3, uint8_t M=0)
{
	//taken from CompressionAlgorithms.C in the ASW source code
	
	if ( K > 7 || M > 7 || (K + M) > 8)
	{
		cout<<"Error: K or M value invalid,  K <=7, M<=7 and K+M<=8 "<<endl;
		return 0xff;
	}
	uint8_t out_val;
	uint8_t exponent = 1;
	uint8_t mantissa =0;
	//cout<<"Encode:"<<endl;
	//printf("Inval:0x%08x\n",in_val);

	// check if V < 2^(M+1)
	if (in_val < ((uint32_t)1 << (M + 1)))
	{
		// set C = V and skip
		out_val = (uint8_t)in_val;
	}
	else
	{
		// V >= 2^(M+1),
		while (in_val > (((uint32_t)1 << (M + 1)) - 1))
		{
			// shift V right until 1's (if any) appear only in LS (M+1) bits
			in_val >>= 1;
			// exponent is number of shifts + 1
			exponent++;
		}

		// cross check for exponent size
		if (exponent > ((1 << K) - 1))
		{
			cout<<"Exponent size  invalid "<<((1<<K)-1)<<endl;
			return 0xff;
		}
		//printf("Input value after shift:0x%08x\n",in_val);

		// mantissa, LS M bits of the shifted value
		mantissa = (uint8_t)(in_val & (((uint32_t)1 << M) - 1));
		//only keep M bits
		// C = m + 2^M * e
		out_val = (uint8_t)(mantissa + (exponent << M));
	}

//	printf("Mantissa:0x%02x\n",mantissa);
//	printf("Exp:0x%02x\n",exponent);

//	cout<<(unsigned int)mantissa<<" "<<(unsigned int)exponent<<" "<<(unsigned int)out_val<<endl;
//	printf("encode:0x%02x\n",(unsigned int)out_val);
	return out_val;
}

uint32_t decode(uint8_t val, uint8_t K, uint8_t M)
{
	uint8_t temp=1<<(M+1);
	if(val<temp)
	{
		return val;
	}
	uint8_t mask=(1<<M)-1;
	uint8_t mask2=(1<<M);

	uint8_t mantissa=val&mask;
	uint8_t exponent=(val>>M)-1;

	printf("mantissa, exponent:%d %d\n",mantissa,exponent);

//	printf("mask:%0x\n",mask);
	uint32_t low=0;
	uint32_t high=0;
	uint32_t real_mantissa= mask2|mantissa ;
	low=real_mantissa<<exponent;
	high=(low|((1<<exponent)-1));
	uint32_t mean=(low+high)>>1;
	
	printf("Low, high, mean:%d %d %d\n",low,high,mean);
	
	return mean;
}

int main(int argc, char *argv[])
{
	uint8_t K=4;
	uint8_t M=4;
//	cout<<"K:"<<(unsigned int)K<<" M: "<<(unsigned int)M<<endl;

	for(uint32_t i=0;i<256;i++)
	{
//cout<<"Test: "<<(unsigned int)i<<endl;
	//	uint8_t out=CompressionAlgorithms_compressS0(i, K,M);
//		cout<<"Decode:"<<decode(out,K,M)<<endl;
		cout<<"------------------------------------"<<endl;
//		uint32_t i=64;
	//	decode(i,K,M);
		cout<<i<<" "<<decode(i,K,M)<<endl;
	}


	return 0;
} 
