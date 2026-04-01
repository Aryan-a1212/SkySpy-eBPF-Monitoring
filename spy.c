#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// Defining a Hash Map to store process execution counts
BPF_HASH(counts, u32, u64);

// This function hooks into the sys_execve system call
int kprobe__sys_execve(struct pt_regs *ctx) {
    u32 key = 0; // Using index 0 to store global execution count
    u64 *val, next_val = 1;

    // Lookup current value in the map
    val = counts.lookup(&key);
    
    if (val) {
        next_val = *val + 1;
    }

    // Atomic update to ensure zero-copy efficiency
    counts.update(&key, &next_val);
    
    return 0;
}
