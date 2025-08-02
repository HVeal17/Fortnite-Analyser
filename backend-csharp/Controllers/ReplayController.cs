using Microsoft.AspNetCore.Mvc;

namespace backend_csharp.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ReplayController : ControllerBase
    {
        [HttpPost("analyze")]
        [RequestSizeLimit(512 * 1024 * 1024)] // up to 512MB
        public async Task<IActionResult> Analyze([FromForm] IFormFile replay)
        {
            if (replay == null || replay.Length == 0)
                return BadRequest(new { error = "No replay file uploaded." });

            var replayDir = Path.Combine(AppContext.BaseDirectory, "Replays");
            Directory.CreateDirectory(replayDir);
            var savePath = Path.Combine(replayDir, Path.GetRandomFileName() + ".replay");

            await using (var fs = System.IO.File.Create(savePath))
            {
                await replay.CopyToAsync(fs);
            }

            // TODO: Parse replay here. For now, mock a minimal result.
            // Later: integrate a Fortnite replay reader to extract real data.
            var result = new
            {
                matchId = Path.GetFileNameWithoutExtension(savePath),
                map = "Asteria",            // example
                fps = 60,
                durationSec = 900,          // example
                player = new { name = "You", placements = 16 },
                stats = new {
                    elims = 8,
                    damageDone = 1361,
                    damageTaken = 345,
                    accuracyPct = 19.0,
                    buildsPlaced = 527,
                    buildsEdited = 80,
                    avgEditMs = 167
                },
                timeline = new [] {
                    new { t= 361.2, type="fight_start" },
                    new { t= 373.4, type="fight_end" },
                },
                heat = new [] { new { x=5123, y=8742, t=120.0 }, new { x=6000, y=9000, t=122.0 } }
            };

            return Ok(result);
        }
    }
}
