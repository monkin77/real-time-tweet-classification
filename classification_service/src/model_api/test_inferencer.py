from inferencer import predict

# Non-Disaster Prediction Example
non_disaster_net_output = predict("This is a normal day.")  # Example usage, replace with actual text
# Ensure to handle the output as needed, e.g.,
print("Non-Disaster Prediction output:", non_disaster_net_output)  # Display the prediction result

disaster_net_output = predict("Forest Fire breaking out...")  # Example usage, replace with actual text
# Ensure to handle the output as needed, e.g., print or log the result.
print("Disaster Prediction output:", disaster_net_output)  # Display the prediction result