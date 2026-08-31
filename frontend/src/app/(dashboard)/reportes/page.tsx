'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { FileText, Download, Sparkles, Send, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
}

export default function ReportesPage() {
  const [generating, setGenerating] = useState(false);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'bot', text: 'Hola, soy M-11 AI. Pregúntame sobre normativas de seguridad minera, procedimientos en frentes de extracción o cómo interpretar alertas de riesgo.' }
  ]);

  const handleGenerateReport = async (format: string = 'pdf') => {
    setGenerating(true);
    setGeneratedFile(null);
    try {
      const res = await api.post(`/reports?format=${format}`);
      setGeneratedFile(res.data.filename);
    } catch (err) {
      console.error('Error generando reporte:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!generatedFile) return;
    try {
      const response = await api.get(`/reports/${generatedFile}/download`, {
        responseType: 'blob',
      });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', generatedFile);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error('Error al descargar el reporte:', err);
    }
  };

  const handleChat = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsg = chatInput.trim();
    setChatInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatLoading(true);

    try {
      const res = await api.post('/gemini/chat', { message: userMsg });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Error al conectar con el asistente de IA. Verifica la configuración de GEMINI_API_KEY.' }]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading]);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Reportes e Inteligencia Artificial</h2>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Report Generator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Generador de Reportes PDF
            </CardTitle>
            <CardDescription>
              Genera un reporte de las últimas 50 alertas y eventos de seguridad del turno actual.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-2">
              <p className="text-sm font-medium">El reporte incluirá:</p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Resumen de alertas por nivel de riesgo</li>
                <li>Tabla cronológica de eventos</li>
                <li>Estadísticas del turno</li>
                <li>Fecha y hora de generación</li>
              </ul>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => handleGenerateReport('pdf')}
                disabled={generating}
                className="w-full flex-1"
              >
                {generating ? (
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                ) : (
                  <FileText className="mr-2 h-4 w-4" />
                )}
                PDF
              </Button>
              <Button
                onClick={() => handleGenerateReport('excel')}
                disabled={generating}
                className="w-full flex-1"
                variant="outline"
              >
                {generating ? (
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                ) : (
                  <FileText className="mr-2 h-4 w-4 text-green-600" />
                )}
                Excel
              </Button>
              <Button
                onClick={() => handleGenerateReport('word')}
                disabled={generating}
                className="w-full flex-1"
                variant="outline"
              >
                {generating ? (
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                ) : (
                  <FileText className="mr-2 h-4 w-4 text-blue-600" />
                )}
                Word
              </Button>
            </div>

            {generatedFile && (
              <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-emerald-400" />
                  <div>
                    <p className="text-sm font-medium text-emerald-400">Reporte generado</p>
                    <p className="text-xs text-muted-foreground truncate max-w-[180px]">{generatedFile}</p>
                  </div>
                </div>
                <Button size="sm" variant="outline" onClick={handleDownload} className="border-emerald-500/50 text-emerald-400">
                  <Download className="h-4 w-4 mr-1" />
                  Descargar
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Chatbot */}
        <Card className="flex flex-col min-h-[500px]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              Asistente de Seguridad IA
              <Badge variant="outline" className="text-xs ml-auto">Gemini</Badge>
            </CardTitle>
            <CardDescription>
              Consulta sobre normativas de seguridad minera, procedimientos de emergencia y análisis de riesgos.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col flex-1 gap-3">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-3 max-h-[300px] pr-1">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-2xl px-3 py-2 max-w-[85%] text-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-sm'
                      : 'bg-muted text-foreground rounded-tl-sm'
                  }`}>
                    {msg.role === 'bot' ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-headings:my-1 prose-ul:my-1 prose-li:my-0">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    ) : (
                      <p>{msg.text}</p>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl rounded-tl-sm px-3 py-2 text-sm text-muted-foreground">
                    <span className="animate-pulse">Pensando...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <form onSubmit={handleChat} className="flex gap-2 mt-auto">
              <Input
                placeholder="¿Cuál es el protocolo ante una alerta ALTO?"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={chatLoading}
                className="flex-1"
              />
              <Button type="submit" size="icon" disabled={!chatInput.trim() || chatLoading}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
