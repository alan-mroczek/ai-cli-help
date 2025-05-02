# Command Helper Configuration

## General Info

- System: Ubuntu 24.04.2 LTS
- Using wifi network
- Development machine with python, node etc.

## Model Examples

### OpenAI (Default)
```
aih --model openai/gpt-4o-mini find all png files
aih --model openai/gpt-4 count files by extension
```

### Ollama (Local Models)
```
aih --model ollama/llama3 convert pdf to png
aih --model ollama/codellama find git commits by author
```

### Gemini (Google AI)
```
aih --model gemini/gemini-1.5-pro search for large log files
aih --model gemini/gemini-1.5-flash show disk usage by directory
```

## Blacklist

rm -rf /
shutdown
reboot
