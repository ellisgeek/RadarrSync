# RadarrSync 
RadarrSync Syncs two Radarr servers through web API. This is a modified version designed to be run in a docker container. This version supports only two servers.

## How to Run
Pull the docker image from
https://cloud.docker.com/repository/docker/dmanius/radarrsync-docker

You need to pass in the following environment variables:
- RADARR_URL -> The endpoint of your radarr server
- RADARR_KEY -> The API key for your radarr server
- RADARR4K_URL -> The endpoint of your radarr server you want to sync to
- RADARR4K_KEY -> The API key for this server
- RADARR_FOLDER -> The Path where HD movies are saved
- RADARR4K_FOLDER -> The Path where 4K movies are saved
- PROFILE_ID -> The profile number you want the video to transcode to

## Example docker-compose.yml
```yaml
# radarrsync  
radarsync: 
  container_name: radarrsync
  image: dmanius/radarrsync-docker
  environment: 
    - RADARR_URL=http://radarr:7878/radarr
    - RADARR_KEY=your api key here
    - RADARR_FOLDER=/media/movies
    - RADARR4K_URL=http://radarr-4k:7878/radarr4k
    - RADARR4K_KEY=your api key here
    - RADARR4K_FOLDER=/media/movies-4k
    - PROFILE_ID=5
restart: always
```
## Notes
 * Ensure that the root path is the same on both servers. ie /movie
