import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { errorMessage } from "../api/client";
import { parcelsApi } from "../api/parcels";
import type { ChatMessagePayload } from "../api/types";
import { ChatIcon, SendIcon } from "../components/icons";
import { useToast } from "../hooks/useToast";

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  text: string;
}

interface AskPayload {
  question: string;
  history: ChatMessagePayload[];
}

const suggestions = [
  "Можно ли отправить ноутбук?",
  "Какой максимальный вес посылки?",
  "Сколько составит таможенная пошлина?",
  "Расскажи что-нибудь интересное",
];

export function SupportPage() {
  const { notify } = useToast();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const nextId = useRef(1);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const askMutation = useMutation({
    mutationFn: ({ question, history }: AskPayload) =>
      parcelsApi.askSupport(question, history),
    onSuccess: (data) => {
      setMessages((current) => [
        ...current,
        { id: nextId.current++, role: "assistant", text: data.answer },
      ]);
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, askMutation.isPending]);

  const send = (text: string) => {
    const trimmed = text.trim();

    if (!trimmed || askMutation.isPending) {
      return;
    }

    // Передаем последние реплики, чтобы ассистент понимал продолжение разговора
    const history: ChatMessagePayload[] = messages.slice(-10).map((message) => ({
      role: message.role,
      content: message.text,
    }));

    setMessages((current) => [
      ...current,
      { id: nextId.current++, role: "user", text: trimmed },
    ]);
    setQuestion("");
    askMutation.mutate({ question: trimmed, history });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    send(question);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Поддержка
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          ИИ-ассистент ответит на вопросы о доставке (вес, электроника, пошлины)
          и поддержит разговор на любую тему.
        </p>
      </div>

      <div className="card flex h-[65vh] min-h-[420px] flex-col overflow-hidden">
        <div className="flex items-center gap-3 border-b border-slate-100 px-5 py-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
            <ChatIcon className="h-5 w-5" />
          </span>
          <div>
            <p className="text-sm font-medium text-slate-900">Ассистент Shipping Service</p>
            <p className="text-xs text-slate-500">
              Правила доставки и свободная беседа
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
          {messages.length === 0 && !askMutation.isPending && (
            <div className="space-y-4">
              <p className="text-sm text-slate-500">
                Спросите о правилах доставки или просто поговорите:
              </p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-sm text-slate-600 transition-colors hover:border-indigo-300 hover:text-indigo-700"
                    onClick={() => send(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={[
                  "max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                  message.role === "user"
                    ? "rounded-br-md bg-indigo-600 text-white"
                    : "rounded-bl-md bg-slate-100 text-slate-800",
                ].join(" ")}
              >
                {message.text}
              </div>
            </div>
          ))}

          {askMutation.isPending && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-slate-100 px-4 py-3">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.2s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.1s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <form
          className="flex items-center gap-2 border-t border-slate-100 px-4 py-3"
          onSubmit={handleSubmit}
        >
          <input
            className="input"
            placeholder="Напишите сообщение…"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            maxLength={500}
          />
          <button
            type="submit"
            className="btn-primary shrink-0"
            disabled={askMutation.isPending || !question.trim()}
            aria-label="Отправить вопрос"
          >
            <SendIcon className="h-4 w-4" />
            <span className="hidden sm:inline">Отправить</span>
          </button>
        </form>
      </div>

      <p className="text-center text-xs text-slate-400">
        Ответы ассистента носят справочный характер и не заменяют официальные
        правила перевозчика.
      </p>
    </div>
  );
}
