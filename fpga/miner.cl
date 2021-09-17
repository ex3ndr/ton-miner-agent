#define RANDOM_SIZE 32
#define SEED_SIZE 16
#define OFFSET_1 0
#define OFFSET_2 12

void data_init(__global __const u32 *data, u32 *head, u32 *tail) {
  for(int i = 0; i<16; i++) {
    head[i] = hc_swap32_S(data[i]);
  }
  for(int i = 0; i<16; i++) {
    tail[i] = hc_swap32_S(data[i+16]);
  }
}

void data_export_random(u32 *tail, __global u8 *random) {
  u8 *tail_8 = (u8*)tail;
  for(int i = 0; i < RANDOM_SIZE; i++) {
    random[i] = tail_8[i + 27];
  }
}

void data_finalize(u32 *tail, u64 index) {
  u32 index_a = index & 0xffffffff;
  u32 index_b = (index >> 4) & 0xffffffff;
  tail[OFFSET_1] = tail[OFFSET_1] ^ index_a;
  tail[OFFSET_1+1] = tail[OFFSET_1+1] ^ index_b;
  tail[OFFSET_2] = tail[OFFSET_2] ^ index_a;
  tail[OFFSET_2+1] = tail[OFFSET_2+1] ^ index_b;

  for(int i = 0; i < 16; i++) {
    tail[i] = hc_swap32_S(tail[i]);
  }
}

sha256_ctx_t miner_init(u32 *head) {
  sha256_ctx_t ctx;
  sha256_init(&ctx);
  sha256_update(&ctx, head, 64);
  return ctx;
}

sha256_ctx_t miner_apply(sha256_ctx_t ctx, u32 *tail, u64 index) {
  u32 index_a = index & 0xffffffff;
  u32 index_b = (index >> 4) & 0xffffffff;

  tail[OFFSET_1] = tail[OFFSET_1] ^ index_a;
  tail[OFFSET_1+1] = tail[OFFSET_1+1] ^ index_b;
  tail[OFFSET_2] = tail[OFFSET_2] ^ index_a;
  tail[OFFSET_2+1] = tail[OFFSET_2+1] ^ index_b;

  sha256_update(&ctx, tail, 59);
  sha256_final(&ctx);

  tail[OFFSET_1] = tail[OFFSET_1] ^ index_a;
  tail[OFFSET_1+1] = tail[OFFSET_1+1] ^ index_b;
  tail[OFFSET_2] = tail[OFFSET_2] ^ index_a;
  tail[OFFSET_2+1] = tail[OFFSET_2+1] ^ index_b;

  return ctx;
}

int memcmp (const u32 *a, const u32 *b, int count) {
  const uchar *s1 = (uchar *)a;
  const uchar *s2 = (uchar *)b;
  while (count-- > 0) {
   if (*s1++ != *s2++)
     return s1[-1] < s2[-1] ? -1 : 1;
  }
  return 0;
}

__kernel void do_work(__global __const u32 *data, __global u32 *output, __global u8 *output_random, u64 offset, u32 iterations) {
  u32 current_id = get_global_id(0);

  // Prepare data
  u32 head[16];
  u32 tail[16];
  data_init(data, head, tail);

  // Latest
  u32 latest[8];
  u64 latest_index;
  latest[0] = 4294967294;
  latest[1] = 4294967294;
  latest[2] = 4294967294;
  latest[3] = 4294967294;
  latest[4] = 4294967294;
  latest[5] = 4294967294;
  latest[6] = 4294967294;
  latest[7] = 4294967294;
  u32 current[8];
  u64 index = offset + ((u64)current_id) * ((u64)iterations);

  // Prepare
  sha256_ctx_t ctx0 = miner_init(head);

  for(int i = 0; i<iterations; i++) {
          
    // Mine
    sha256_ctx_t ctx = miner_apply(ctx0, tail, index);

    // Output
    current[0] = hc_swap32_S(ctx.h[0]);
    current[1] = hc_swap32_S(ctx.h[1]);
    current[2] = hc_swap32_S(ctx.h[2]);
    current[3] = hc_swap32_S(ctx.h[3]);
    current[4] = hc_swap32_S(ctx.h[4]);
    current[5] = hc_swap32_S(ctx.h[5]);
    current[6] = hc_swap32_S(ctx.h[6]);
    current[7] = hc_swap32_S(ctx.h[7]);

    if (memcmp(current, latest, 32) < 0) {
      latest_index = index;
      latest[0] = current[0];
      latest[1] = current[1];
      latest[2] = current[2];
      latest[3] = current[3];
      latest[4] = current[4];
      latest[5] = current[5];
      latest[6] = current[6];
      latest[7] = current[7];
    }

    index++;
  }
  
  // Export output
  output[current_id * 8 + 0] = latest[0];
  output[current_id * 8 + 1] = latest[1];
  output[current_id * 8 + 2] = latest[2];
  output[current_id * 8 + 3] = latest[3];
  output[current_id * 8 + 4] = latest[4];
  output[current_id * 8 + 5] = latest[5];
  output[current_id * 8 + 6] = latest[6];
  output[current_id * 8 + 7] = latest[7];

  // Preprocess data
  data_finalize(tail, latest_index);
  
  // Export random
  data_export_random(tail, output_random + current_id * RANDOM_SIZE);
}

__kernel void do_work_debug(__global __const u32 *data, __global u32 *output, __global u8 *output_random, __global u32 *output_data, __global u32 *output_debug, u32 iter) {

  // Latest
  u32 latest[8];
  u64 latest_index;
  u32 current[8];
  u64 index = 5000000000;

  latest[0] = 4294967294;
  latest[1] = 4294967294;
  latest[2] = 4294967294;
  latest[3] = 4294967294;
  latest[4] = 4294967294;
  latest[5] = 4294967294;
  latest[6] = 4294967294;
  latest[7] = 4294967294;

  // Copy data
  u32 head[16];
  u32 tail[16];
  data_init(data, head, tail);

  // SHA256
  sha256_ctx_t ctx0 = miner_init(head);

  for(int i = 0; i<iter; i++) {

    // Mine
    sha256_ctx_t ctx = miner_apply(ctx0, tail, index);
    
    // Output
    current[0] = hc_swap32_S(ctx.h[0]);
    current[1] = hc_swap32_S(ctx.h[1]);
    current[2] = hc_swap32_S(ctx.h[2]);
    current[3] = hc_swap32_S(ctx.h[3]);
    current[4] = hc_swap32_S(ctx.h[4]);
    current[5] = hc_swap32_S(ctx.h[5]);
    current[6] = hc_swap32_S(ctx.h[6]);
    current[7] = hc_swap32_S(ctx.h[7]);

    output_debug[i * 8 + 0] = current[0];
    output_debug[i * 8 + 1] = current[1];
    output_debug[i * 8 + 2] = current[2];
    output_debug[i * 8 + 3] = current[3];
    output_debug[i * 8 + 4] = current[4];
    output_debug[i * 8 + 5] = current[5];
    output_debug[i * 8 + 6] = current[6];
    output_debug[i * 8 + 7] = current[7];

    if (memcmp(current, latest, 32) < 0) {
      latest_index = index;
      latest[0] = current[0];
      latest[1] = current[1];
      latest[2] = current[2];
      latest[3] = current[3];
      latest[4] = current[4];
      latest[5] = current[5];
      latest[6] = current[6];
      latest[7] = current[7];
    }

    // Update index
    index++;
  }
  
  output[0] = latest[0];
  output[1] = latest[1];
  output[2] = latest[2];
  output[3] = latest[3];
  output[4] = latest[4];
  output[5] = latest[5];
  output[6] = latest[6];
  output[7] = latest[7];

  // Prepocess data
  data_finalize(tail, latest_index);
  
  // Export Random
  data_export_random(tail, output_random);
  
  // Export data
  for(int i = 0; i < 16; i++){
    output_data[i] = hc_swap32_S(head[i]);
  }
  for(int i = 0; i < 16; i++){
    output_data[16+i] = tail[i]; // Already swapped
  }
}