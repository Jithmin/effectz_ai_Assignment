using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

public class CartListController : Controller
{
    private readonly string _filePath = Path.Combine(Directory.GetCurrentDirectory(), "cart_items.json");

    public IActionResult Index()
    {
        return View();
    }

    [HttpPost]
    public IActionResult SaveList([FromBody] List<CartItem> items)
    {
        var json = JsonSerializer.Serialize(items, new JsonSerializerOptions { WriteIndented = true });
        System.IO.File.WriteAllText(_filePath, json);
        return Ok(new { message = "Saved", count = items.Count });
    }
}