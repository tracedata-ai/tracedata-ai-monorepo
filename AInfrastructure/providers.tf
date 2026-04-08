terraform {
  required_version = ">= 1.4.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region     = "ap-south-1"   # Change to your desired AWS region
  access_key = "xxxxxxxxxxxx" # Replace with your access key
  secret_key = "xxxxxxxxxxxx" # Replace with your secret key
}
