#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__  = (
    'wrtyis@outlook.com'
	)

__license__ = 'GPLv3'
__version__ = '0.0.1'

"""
ASS 字幕格式规范:
https://github.com/weizhenye/ASS/wiki/ASS-字幕格式规范

"""

""" 
鸣谢:
https://archive.org/details/youtubeannotations

"""

#祝 Google 早日亲妈爆炸!

import argparse
import xml.etree.ElementTree
import sys

class info(object):
    def __init__(self):
        self.HEAD = "[Script Info]\n"\
                    "; Script generated by Annotations2Sub\n"\
                    "; https://github.com/WRTYis/Annotations2Sub\n"

        self.data={
            'Title':'Default File',
            'ScriptType':'v4.00+',
            'WrapStyle':'0',
            'ScaledBorderAndShadow':'yes',
            'YCbCr Matrix':'None',
            'PlayResX':'1920',
            'PlayResY':'1080'}

    def change(self,Title=None,PlayResX=None,PlayResY=None):
        for k,v in {'Title':Title,'PlayResX':PlayResX,'PlayResY':PlayResY}.items():
            if v is not None:
                self.data[k]=v
    
    def dump(self):
        data = self.HEAD
        for k, v in self.data.items():
            data += str(k)+': '+str(v)+'\n' 
        return data

class style(object):
    def __init__(self):
        self.HEAD = "\n"\
                    "[V4+ Styles]\n"\
                    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        self.data = {}
        self.add(Name='Default')
    
    def add(self,Name,Fontname='Arial',Fontsize=20,PrimaryColour='&H00FFFFFF',SecondaryColour='&H000000FF',OutlineColour='&H6B000000',BackColour='&HAB000000',Bold=0,Italic=0,Underline=0,StrikeOut=0,ScaleX=100,ScaleY=100,Spacing=0,Angle=0,BorderStyle=3,Outline=2,Shadow=0,Alignment=2,MarginL=10,MarginR=10,MarginV=10,Encoding=1):
        self.data[Name] = [Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding]

    def change(self,Name,Fontname=None,Fontsize=None,PrimaryColour=None,SecondaryColour=None,OutlineColour=None,BackColour=None,Bold=None,Italic=None,Underline=None,StrikeOut=None,ScaleX=None,ScaleY=None,Spacing=None,Angle=None,BorderStyle=None,Outline=None,Shadow=None,Alignment=None,MarginL=None,MarginR=None,MarginV=None,Encoding=None):
        for i,v in enumerate([Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding]):
            if v is not None:
                self.data[Name][i] = v

    def dump(self):
        data = self.HEAD
        for k, v in self.data.items():
            data += 'Style: ' + str(k) +','
            for i,d in enumerate(v):
                if i == 21:
                    data += str(d)
                else:
                    data += str(d) + ','
            data +=  '\n'
        return data

class event(object):
    def __init__(self):
        self.HEAD = "\n"\
                    "[Events]\n"\
                    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        self.data = []

    def add(self,Layer=0, Start='0:00:00.00', End='0:00:00.00', Style='Default', Name='', MarginL=0, MarginR=0, MarginV=0, Effect='',Text=''):
        self.data.append([Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text])

    def dump(self):
        data = self.HEAD
        for v in self.data:
            data += 'Dialogue: '
            for i,d in enumerate(v):
                if i == 9:
                    data += str(d)
                else:
                    data += str(d) + ','
            data +='\n'
        return data

class Annotations2Sub():
    def __init__(self,string,Title='默认文件',PlayResX=1920,PlayResY=1080,Zoom=1):
        self.info = info()
        self.style = style()
        self.event = event()
        self.xml = xml.etree.ElementTree.fromstring(string)
        self.info.change(Title,PlayResX,PlayResY)
        self.style.change(Name='Default',ScaleX=PlayResX/1280*100*Zoom,ScaleY=PlayResY/720*100*Zoom)
        self.Zoom = Zoom
        self._convert(self.xml) 

    def save(self,File):
        with open(File+'.ass', 'w',encoding='utf-8') as f:
            f.write(self.info.dump())
            f.write(self.style.dump())
            f.write(self.event.dump())

    def _convert(self,string):
        for each in self.xml.find('annotations').findall('annotation'):
            
            #处理 annotation id
            Name = each.get('id')
            
            #处理文本
            Text = each.find('TEXT')
            if Text is not None:
                Text = Text.text.replace('\n',r'\N')
            else:
                Text = ''

            try:
                _Segment = each.find('segment').find('movingRegion').findall('rectRegion')

                #处理时间
                Start = min(_Segment[0].get('t'), _Segment[1].get('t'))
                End = max(_Segment[0].get('t'), _Segment[1].get('t'))
                if "never" in (Start, End):
                    continue
                
                #处理位置
                '''
                    x,y: 文本框左上角的坐标
                    w,h: 文本框的宽度和高度 (TODO)
                '''
                (x, y, w, h) = map(float,(_Segment[0].get(i) for i in ('x','y','w','h')))
            except:
                if not _Segment:
                    _Segment = each.find('segment').find('movingRegion').findall('anchoredRegion')
                if not _Segment:
                    continue
            
            #处理颜色
            if each.find('appearance') is not None:
                if each.find('appearance').get('fgColor') is not '0':
                    PrimaryColour = r'&H'+str(hex(int(each.find('appearance').get('fgColor')))).replace('0x','')
                else:
                    PrimaryColour = r'&HFFFFFF'
                if each.find('appearance').get('bgColor') is not '0':
                    BackColour = r'&H'+str(hex(int(each.find('appearance').get('bgColor')))).replace('0x','')
                else:
                    BackColour = r'&H000000'
            else:
                PrimaryColour = r'&HFFFFFF'
                BackColourBackColour = r'&H000000'
            
            #提交
            self.event.add(Start=Start,End=End,Name=Name,Text=self._tab_helper(Text=Text,PrimaryColour=PrimaryColour,BackColour=BackColour,x=x,y=y,Zoom=self.Zoom))

    def _tab_helper(self,Text,PrimaryColour=None,BackColour=None,x=None,y=None,Zoom=1):
        _pos = "\\pos({},{})".format(str(int(float(x)*10/Zoom)),str(int(float(y)*10/Zoom)))
        _c = r'\c'+PrimaryColour
        _3c = r'\3c'+BackColour
        _tab = r'\an7' + _pos + _c + _3c
        _Text = "{%s}" % _tab + Text
        return _Text
        #{\2c&H2425DA&\pos(208,148)}test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='一个可以把Youtube注释转换成ASS字幕的脚本')
    parser.add_argument('File',type=str,help='待转换的文件',)
    parser.add_argument('--PlayResX=',default=1920,type=int,help='视频宽度,默认是1920',dest='PlayResX')
    parser.add_argument('--PlayResY=',default=1080,type=int,help='视频高度,默认是1080',dest='PlayResY')
    parser.add_argument('--Zoom=',default=1,type=float,help='缩放系数,默认是1',dest='Zoom')
    args = parser.parse_args()
    ass = Annotations2Sub(string=open(args.File,'r',encoding="utf-8").read(),Title=args.File,PlayResX=args.PlayResX,PlayResY=args.PlayResY,Zoom=args.Zoom)
    ass.save(File=args.File)
    print("Done.")