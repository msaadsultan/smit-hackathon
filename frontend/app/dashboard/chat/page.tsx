'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/utils/api';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

interface Student {
  id: string;
  name: string;
  email: string;
}

export default function ChatPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      fetchMessages();
    }
  }, [selectedStudent]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchStudents = async () => {
    try {
      const response = await api.get('/students');
      setStudents(response.data);
    } catch (error) {
      console.error('Failed to fetch students:', error);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/chat/${selectedStudent}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedStudent) return;

    const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user' as const,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/${selectedStudent}/stream?message=${encodeURIComponent(
          input
        )}`
      );

      let assistantMessage = '';

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.content) {
          assistantMessage += data.content;
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.role === 'assistant') {
              lastMessage.content = assistantMessage;
            } else {
              newMessages.push({
                id: Date.now().toString(),
                content: assistantMessage,
                role: 'assistant',
                timestamp: new Date().toISOString(),
              });
            }
            return newMessages;
          });
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsLoading(false);
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-6rem)]">
      <div className="w-64 border-r border-gray-200 p-4">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Students</h2>
        <div className="space-y-2">
          {students.map((student) => (
            <button
              key={student.id}
              onClick={() => setSelectedStudent(student.id)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                selectedStudent === student.id
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {student.name}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedStudent ? (
          <>
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === 'assistant' ? 'justify-start' : 'justify-end'
                    }`}
                  >
                    <div
                      className={`max-w-lg rounded-lg px-4 py-2 ${
                        message.role === 'assistant'
                          ? 'bg-gray-100'
                          : 'bg-indigo-600 text-white'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs mt-1 opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            <div className="p-4 border-t border-gray-200">
              <form onSubmit={handleSubmit} className="flex space-x-4">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a student to start chatting
          </div>
        )}
      </div>
    </div>
  );
}