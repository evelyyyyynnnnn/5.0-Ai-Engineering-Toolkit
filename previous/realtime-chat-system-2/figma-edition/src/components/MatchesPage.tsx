import { ImageWithFallback } from './figma/ImageWithFallback';
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Coffee, MessageCircle, Heart, Calendar, MapPin, Clock } from "lucide-react";

interface Match {
  id: string;
  name: string;
  age: number;
  photo: string;
  lastMessage?: string;
  timestamp: string;
  unread: boolean;
  location: string;
  status: 'new_match' | 'chatting' | 'planning' | 'scheduled';
  matchedOn: string;
}

interface MatchesPageProps {
  onChatClick: (matchId: string) => void;
}

export function MatchesPage({ onChatClick }: MatchesPageProps) {
  // Mock matches data
  const matches: Match[] = [
    {
      id: "match1",
      name: "Olivia",
      age: 28,
      photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      lastMessage: "太好了！明天下午三点在三里屯星巴克见面吧 ☕",
      timestamp: "刚刚",
      unread: true,
      location: "三里屯",
      status: "scheduled",
      matchedOn: "2天前"
    },
    {
      id: "match2",
      name: "Ryan",
      age: 32,
      photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      lastMessage: "你推荐的那家咖啡店在哪里？我想试试",
      timestamp: "3小时前",
      unread: false,
      location: "国贸",
      status: "chatting",
      matchedOn: "1周前"
    },
    {
      id: "match3",
      name: "Zoe",
      age: 26,
      photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      timestamp: "1天前",
      unread: false,
      location: "望京",
      status: "new_match",
      matchedOn: "1天前"
    }
  ];

  const getStatusBadge = (status: Match['status']) => {
    switch (status) {
      case 'new_match':
        return <Badge className="bg-pink-100 text-pink-800">新匹配</Badge>;
      case 'chatting':
        return <Badge variant="secondary">聊天中</Badge>;
      case 'planning':
        return <Badge className="bg-blue-100 text-blue-800">计划中</Badge>;
      case 'scheduled':
        return <Badge className="bg-green-100 text-green-800">已约定</Badge>;
      default:
        return null;
    }
  };

  const getStatusIcon = (status: Match['status']) => {
    switch (status) {
      case 'new_match':
        return <Heart className="w-4 h-4 text-pink-600" />;
      case 'chatting':
        return <MessageCircle className="w-4 h-4 text-blue-600" />;
      case 'planning':
        return <Coffee className="w-4 h-4 text-orange-600" />;
      case 'scheduled':
        return <Calendar className="w-4 h-4 text-green-600" />;
      default:
        return null;
    }
  };

  const newMatches = matches.filter(match => match.status === 'new_match');
  const conversations = matches.filter(match => match.status !== 'new_match');

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Heart className="w-6 h-6 text-pink-600" />
              <h1 className="text-xl">匹配</h1>
            </div>
            <div className="flex gap-2">
              {newMatches.length > 0 && (
                <Badge variant="destructive" className="rounded-full">
                  {newMatches.length} 新匹配
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto">
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mx-4 mt-4">
            <TabsTrigger value="all">全部</TabsTrigger>
            <TabsTrigger value="new">新匹配</TabsTrigger>
            <TabsTrigger value="conversations">对话</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-4">
            {matches.length === 0 ? (
              <div className="p-8 text-center">
                <Heart className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                <h3 className="mb-2">还没有匹配</h3>
                <p className="text-muted-foreground">
                  开始浏览并喜欢其他用户来获得匹配吧！
                </p>
              </div>
            ) : (
              <div className="space-y-4 px-4">
                {/* New Matches Section */}
                {newMatches.length > 0 && (
                  <div>
                    <h3 className="mb-3 flex items-center gap-2">
                      <Heart className="w-5 h-5 text-pink-600" />
                      新匹配 ({newMatches.length})
                    </h3>
                    <div className="grid grid-cols-3 gap-3 mb-6">
                      {newMatches.map((match) => (
                        <Card 
                          key={match.id}
                          className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                          onClick={() => onChatClick(match.id)}
                        >
                          <div className="text-center">
                            <ImageWithFallback
                              src={match.photo}
                              alt={`${match.name}的头像`}
                              className="w-16 h-16 rounded-full object-cover mx-auto mb-2"
                            />
                            <h4 className="text-sm mb-1">{match.name}</h4>
                            <p className="text-xs text-muted-foreground">
                              {match.matchedOn}匹配
                            </p>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Conversations Section */}
                {conversations.length > 0 && (
                  <div>
                    <h3 className="mb-3 flex items-center gap-2">
                      <MessageCircle className="w-5 h-5 text-blue-600" />
                      对话 ({conversations.length})
                    </h3>
                    <div className="space-y-3">
                      {conversations.map((match) => (
                        <Card 
                          key={match.id}
                          className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => onChatClick(match.id)}
                        >
                          <div className="flex gap-3">
                            <div className="relative">
                              <ImageWithFallback
                                src={match.photo}
                                alt={`${match.name}的头像`}
                                className="w-14 h-14 rounded-full object-cover"
                              />
                              {match.unread && (
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full" />
                              )}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2">
                                  <h4>{match.name}, {match.age}</h4>
                                  {getStatusBadge(match.status)}
                                </div>
                                <span className="text-xs text-muted-foreground">
                                  {match.timestamp}
                                </span>
                              </div>
                              
                              <div className="flex items-center text-xs text-muted-foreground mb-2">
                                <MapPin className="w-3 h-3 mr-1" />
                                <span>{match.location}</span>
                                <span className="mx-2">•</span>
                                <span>{match.matchedOn}匹配</span>
                              </div>
                              
                              {match.lastMessage && (
                                <p className={`text-sm truncate ${
                                  match.unread ? 'text-foreground' : 'text-muted-foreground'
                                }`}>
                                  {match.lastMessage}
                                </p>
                              )}
                            </div>

                            <div className="flex flex-col items-center justify-center">
                              {getStatusIcon(match.status)}
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="new" className="mt-4">
            <div className="px-4">
              {newMatches.length === 0 ? (
                <div className="p-8 text-center">
                  <Heart className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                  <h3 className="mb-2">没有新匹配</h3>
                  <p className="text-muted-foreground">
                    继续浏览来获得更多匹配！
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {newMatches.map((match) => (
                    <Card 
                      key={match.id}
                      className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => onChatClick(match.id)}
                    >
                      <div className="text-center">
                        <ImageWithFallback
                          src={match.photo}
                          alt={`${match.name}的头像`}
                          className="w-20 h-20 rounded-full object-cover mx-auto mb-3"
                        />
                        <h4 className="mb-1">{match.name}, {match.age}</h4>
                        <div className="flex items-center justify-center text-xs text-muted-foreground mb-2">
                          <MapPin className="w-3 h-3 mr-1" />
                          <span>{match.location}</span>
                        </div>
                        <Badge className="bg-pink-100 text-pink-800 text-xs">
                          {match.matchedOn}匹配
                        </Badge>
                        <Button className="w-full mt-3" size="sm">
                          <MessageCircle className="w-4 h-4 mr-2" />
                          开始聊天
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="conversations" className="mt-4">
            <div className="px-4 space-y-3">
              {conversations.length === 0 ? (
                <div className="p-8 text-center">
                  <MessageCircle className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                  <h3 className="mb-2">还没有对话</h3>
                  <p className="text-muted-foreground">
                    和你的匹配开始对话，约个咖啡吧！
                  </p>
                </div>
              ) : (
                conversations.map((match) => (
                  <Card 
                    key={match.id}
                    className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => onChatClick(match.id)}
                  >
                    <div className="flex gap-3">
                      <div className="relative">
                        <ImageWithFallback
                          src={match.photo}
                          alt={`${match.name}的头像`}
                          className="w-14 h-14 rounded-full object-cover"
                        />
                        {match.unread && (
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <h4>{match.name}, {match.age}</h4>
                            {getStatusBadge(match.status)}
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {match.timestamp}
                          </span>
                        </div>
                        
                        <div className="flex items-center text-xs text-muted-foreground mb-2">
                          <MapPin className="w-3 h-3 mr-1" />
                          <span>{match.location}</span>
                        </div>
                        
                        {match.lastMessage && (
                          <p className={`text-sm truncate ${
                            match.unread ? 'text-foreground' : 'text-muted-foreground'
                          }`}>
                            {match.lastMessage}
                          </p>
                        )}
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}