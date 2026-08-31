import { useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Separator } from "./ui/separator";
import { MapPin, Clock, Coffee, Bell, Shield, HelpCircle, LogOut } from "lucide-react";

interface SettingsPageProps {
  onBackClick: () => void;
}

export function SettingsPage({ onBackClick }: SettingsPageProps) {
  const [notifications, setNotifications] = useState(true);
  const [location, setLocation] = useState(true);
  const [ageRange, setAgeRange] = useState([22, 35]);
  const [maxDistance, setMaxDistance] = useState([5]);
  const [coffeePreference, setCoffeePreference] = useState("any");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={onBackClick}>
              ←
            </Button>
            <h1 className="text-xl">设置</h1>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {/* Discovery Preferences */}
        <Card className="p-6">
          <h3 className="mb-4">发现偏好</h3>
          
          <div className="space-y-6">
            {/* Age Range */}
            <div>
              <Label className="mb-3 block">年龄范围: {ageRange[0]} - {ageRange[1]} 岁</Label>
              <Slider
                value={ageRange}
                onValueChange={setAgeRange}
                max={60}
                min={18}
                step={1}
                className="w-full"
              />
            </div>

            {/* Distance */}
            <div>
              <Label className="mb-3 block">最大距离: {maxDistance[0]} 公里</Label>
              <Slider
                value={maxDistance}
                onValueChange={setMaxDistance}
                max={50}
                min={1}
                step={1}
                className="w-full"
              />
            </div>

            {/* Coffee Preference */}
            <div>
              <Label className="mb-3 block">咖啡偏好</Label>
              <Select value={coffeePreference} onValueChange={setCoffeePreference}>
                <SelectTrigger>
                  <SelectValue placeholder="选择偏好" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">不限</SelectItem>
                  <SelectItem value="espresso">意式浓缩</SelectItem>
                  <SelectItem value="americano">美式咖啡</SelectItem>
                  <SelectItem value="latte">拿铁</SelectItem>
                  <SelectItem value="cappuccino">卡布奇诺</SelectItem>
                  <SelectItem value="handdrip">手冲咖啡</SelectItem>
                  <SelectItem value="specialty">精品咖啡</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </Card>

        {/* Privacy & Safety */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <Shield className="w-5 h-5 mr-2" />
            <h3>隐私与安全</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>位置服务</Label>
                <p className="text-sm text-muted-foreground">允许应用访问你的位置</p>
              </div>
              <Switch checked={location} onCheckedChange={setLocation} />
            </div>

            <Separator />

            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Shield className="w-4 h-4 mr-2" />
                屏蔽与举报
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <MapPin className="w-4 h-4 mr-2" />
                隐藏距离
              </Button>
            </div>
          </div>
        </Card>

        {/* Notifications */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <Bell className="w-5 h-5 mr-2" />
            <h3>通知设置</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>推送通知</Label>
                <p className="text-sm text-muted-foreground">接收新匹配和消息通知</p>
              </div>
              <Switch checked={notifications} onCheckedChange={setNotifications} />
            </div>

            <Separator />

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>新匹配</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>新消息</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>咖啡提醒</Label>
                <Switch />
              </div>
            </div>
          </div>
        </Card>

        {/* Available Times */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <Clock className="w-5 h-5 mr-2" />
            <h3>空闲时间</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>工作日早上</Label>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <Label>工作日下午</Label>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <Label>工作日晚上</Label>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label>周末</Label>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>

        {/* Help & Support */}
        <Card className="p-6">
          <h3 className="mb-4">帮助与支持</h3>
          
          <div className="space-y-3">
            <Button variant="ghost" className="w-full justify-start">
              <HelpCircle className="w-4 h-4 mr-2" />
              常见问题
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Coffee className="w-4 h-4 mr-2" />
              使用指南
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              联系客服
            </Button>
          </div>
        </Card>

        <Separator />

        {/* Account Actions */}
        <div className="space-y-3 pb-6">
          <Button variant="outline" className="w-full">
            暂停账户
          </Button>
          <Button variant="destructive" className="w-full">
            <LogOut className="w-4 h-4 mr-2" />
            退出登录
          </Button>
        </div>
      </div>
    </div>
  );
}