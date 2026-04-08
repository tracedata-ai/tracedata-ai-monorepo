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
  region  = "ap-south-1"  # Change to your desired AWS region
  access_key = "AKIA2H3EWGHGCISRMR5O"  # Replace with your access key
  secret_key = "IZ/jZIN4mk0qQxona0APu9iebf14TDCdgmCjr1zN"  # Replace with your secret key
}