using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace backend_csharp.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AnalyzeController : ControllerBase
    {
        [HttpPost]
        public async Task<IActionResult> Post([FromForm] IFormFile video)
        {
            if (video == null || video.Length == 0)
                return BadRequest("No video file uploaded.");

            var saveDirectory = Path.Combine(Directory.GetCurrentDirectory(), "Videos");
            Directory.CreateDirectory(saveDirectory);

            var savePath = Path.Combine(saveDirectory, video.FileName);

            using (var stream = System.IO.File.Create(savePath))
            {
                await video.CopyToAsync(stream);
            }

            string ffmpegOutput = RunFFmpeg(savePath);

            var metadata = ParseMetadata(ffmpegOutput);

            return Ok(new
            {
                analysis = "Parsed FFmpeg metadata",
                metadata
            });
        }

        private string RunFFmpeg(string videoPath)
        {
            var ffmpegPath = "ffmpeg"; // Make sure ffmpeg is in PATH
            var arguments = $"-i \"{videoPath}\" -hide_banner";

            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = ffmpegPath,
                    Arguments = arguments,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            process.Start();
            string output = process.StandardError.ReadToEnd();
            process.WaitForExit();

            return output;
        }

        private object ParseMetadata(string output)
{
    string? duration = Extract(output, @"Duration:\s+(\d{2}:\d{2}:\d{2}\.\d{2})");
    string? resolution = Extract(output, @"(\d{3,5}x\d{3,5})");
    string? fps = Extract(output, @"(\d{2,3})\s+fps");
    string? audioBitrate = Extract(output, @"Audio:.*?(\d+\s+kb/s)");

    return new
    {
        duration = duration ?? "Unknown",
        resolution = resolution ?? "Unknown",
        fps = fps ?? "Unknown",
        audio_bitrate = audioBitrate ?? "Unknown"
    };
}


        private string? Extract(string input, string pattern)
        {
            var match = Regex.Match(input, pattern);
            return match.Success ? match.Groups[1].Value : null;
        }
    }
}
