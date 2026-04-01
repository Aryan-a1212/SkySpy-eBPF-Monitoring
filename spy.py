from bcc import BPF
import boto3
import time

# 1. Initialize BPF and Load the C code
b = BPF(src_file="spy.c")
print("🚀 SkySpy is now monitoring kernel events... Press Ctrl+C to stop.")

# 2. Initialize AWS CloudWatch Client
# Ensure your EC2 has an IAM Role with CloudWatch permissions
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def push_to_cloudwatch(value):
    try:
        cloudwatch.put_metric_data(
            Namespace='SkySpy/Metrics',
            MetricData=[
                {
                    'MetricName': 'ProcCalls',
                    'Dimensions': [
                        {'Name': 'InstanceID', 'Value': 'EC2-Monitor-Node'},
                        {'Name': 'Environment', 'Value': 'Production'}
                    ],
                    'Value': value,
                    'Unit': 'Count'
                },
            ]
        )
        print(f"✅ Successfully pushed {value} events to AWS.")
    except Exception as e:
        print(f"❌ AWS Error: {e}")

# 3. Main Loop: Poll every 10 seconds
try:
    while True:
        time.sleep(10)
        
        # Access the BPF Map named 'counts'
        counts = b.get_table("counts")
        
        for key, val in counts.items():
            event_count = val.value
            if event_count > 0:
                push_to_cloudwatch(event_count)
        
        # Reset the map for the next interval
        counts.clear()

except KeyboardInterrupt:
    print("\nStopping SkySpy. Goodbye!")
