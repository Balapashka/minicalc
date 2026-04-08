#!/usr/bin/env python3
"""
YouTube Channel Video Links Parser

This script takes a YouTube channel URL or channel ID and extracts all video links,
saving them to a .txt file.

Usage:
    python youtube_parser.py <channel_url_or_id> [output_file]

Example:
    python youtube_parser.py https://www.youtube.com/@ChannelName
    python youtube_parser.py UCxxxxxxxxxxxxxxxxxxxxxxx channel_videos.txt

Note: You need a YouTube Data API v3 key. Set it via environment variable:
    export YOUTUBE_API_KEY=your_api_key_here
"""

import sys
import os
import re
from googleapiclient.discovery import build


def extract_channel_id(channel_input):
    """
    Extract channel ID from various YouTube channel URL formats or return as-is if already an ID.
    
    Supported formats:
    - https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxx
    - https://www.youtube.com/@ChannelName
    - https://www.youtube.com/c/ChannelName
    - https://www.youtube.com/user/Username
    - UCxxxxxxxxxxxxxxxxxxxxxxx (raw channel ID)
    - @ChannelName (handle)
    """
    channel_input = channel_input.strip()
    
    # Already a channel ID (starts with UC)
    if channel_input.startswith('UC') and len(channel_input) == 24:
        return channel_input
    
    # Format: youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxx
    match = re.search(r'youtube\.com/channel/([a-zA-Z0-9_-]+)', channel_input)
    if match:
        return match.group(1)
    
    # Format: youtube.com/@ChannelName or just @ChannelName
    match = re.search(r'@(?:[a-zA-Z0-9_-]+)', channel_input)
    if match:
        # For handles, we need to resolve them via API first
        return channel_input  # Return as-is, will handle in main function
    
    # Format: youtube.com/c/ChannelName or youtube.com/user/Username
    match = re.search(r'youtube\.com/(?:c|user)/([a-zA-Z0-9_-]+)', channel_input)
    if match:
        return channel_input  # Return as-is, will need resolution
    
    # If nothing matches, assume it's a handle or custom URL that needs resolution
    return channel_input


def get_channel_id_from_api(youtube, channel_input):
    """
    Resolve channel handle, custom URL, or username to actual channel ID using the API.
    """
    # Check if it's already a valid channel ID
    if channel_input.startswith('UC') and len(channel_input) == 24:
        return channel_input
    
    # Try to find by handle (@username)
    if channel_input.startswith('@'):
        handle = channel_input.lstrip('@')
        try:
            # Alternative: try channels.list with forHandle (if available)
            request = youtube.channels().list(
                part='id',
                forHandle=handle
            )
            response = request.execute()
            if response.get('items'):
                return response['items'][0]['id']
        except Exception:
            pass
    
    # Try searching for the channel
    try:
        request = youtube.search().list(
            part='snippet',
            q=channel_input,
            type='channel',
            maxResults=5
        )
        response = request.execute()
        
        if response.get('items'):
            # Return the first matching channel
            return response['items'][0]['id']['channelId']
    except Exception as e:
        print(f"Error searching for channel: {e}")
    
    return None


def get_all_video_ids(youtube, channel_id):
    """
    Retrieve all video IDs from a channel using the YouTube Data API v3.
    Uses pagination to get ALL videos.
    """
    video_ids = []
    next_page_token = None
    
    print(f"Fetching videos from channel: {channel_id}")
    
    while True:
        request = youtube.search().list(
            part='id',
            channelId=channel_id,
            type='video',
            maxResults=50,  # Maximum allowed per request
            pageToken=next_page_token,
            order='date'  # Order by date (newest first)
        )
        
        response = request.execute()
        
        # Extract video IDs
        for item in response.get('items', []):
            if item['id']['kind'] == 'youtube#video':
                video_ids.append(item['id']['videoId'])
        
        print(f"Fetched {len(video_ids)} videos so far...")
        
        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return video_ids


def save_to_file(video_ids, output_filename):
    """
    Save all video URLs to a text file.
    """
    with open(output_filename, 'w', encoding='utf-8') as f:
        for video_id in video_ids:
            f.write(f"https://www.youtube.com/watch?v={video_id}\n")
    
    print(f"\nSuccessfully saved {len(video_ids)} video links to '{output_filename}'")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    channel_input = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'youtube_videos.txt'
    
    # Get API key from environment variable
    api_key = os.environ.get('YOUTUBE_API_KEY')
    
    if not api_key:
        print("ERROR: YouTube API key not found!")
        print("Please set the YOUTUBE_API_KEY environment variable:")
        print("  export YOUTUBE_API_KEY=your_api_key_here")
        print("\nGet an API key at: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    
    try:
        # Build the YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Extract/resolve channel ID
        channel_id = extract_channel_id(channel_input)
        
        # If we couldn't extract a proper ID, try to resolve via API
        if not channel_id.startswith('UC') or len(channel_id) != 24:
            print(f"Resolving channel identifier: {channel_input}")
            resolved_id = get_channel_id_from_api(youtube, channel_input)
            if resolved_id:
                channel_id = resolved_id
                print(f"Resolved to channel ID: {channel_id}")
            else:
                print(f"Could not resolve channel identifier: {channel_input}")
                print("Please provide a valid channel URL or ID.")
                sys.exit(1)
        
        # Get all video IDs
        video_ids = get_all_video_ids(youtube, channel_id)
        
        if not video_ids:
            print("No videos found on this channel.")
            sys.exit(0)
        
        # Save to file
        save_to_file(video_ids, output_file)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have a valid YouTube Data API v3 key.")
        sys.exit(1)


if __name__ == '__main__':
    main()
