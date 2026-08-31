//
//  ProfilePageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct ProfilePageView: View {
    @State private var showingEditProfile = false
    @State private var showingSettings = false
    private let currentUser = MockData.currentUser
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                HStack {
                        Text("Brew")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.black)
                    
                    Spacer()
                    
                    HStack(spacing: 16) {
                        Button(action: { showingSettings = true }) {
                            Image(systemName: "gearshape.fill")
                                .font(.system(size: 20))
                                .foregroundColor(.black)
                        }
                        
                        Button(action: { showingEditProfile = true }) {
                            Image(systemName: "pencil")
                                .font(.system(size: 20))
                                .foregroundColor(.black)
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(Color.white)
                
                VStack(spacing: 16) {
                    // Profile Photo Card
                    Card {
                        VStack(spacing: 16) {
                            ZStack(alignment: .bottomTrailing) {
                                AsyncImageWithFallback(
                                    url: currentUser.photo,
                                    contentMode: .fill
                                )
                                .frame(width: 128, height: 128)
                                .clipShape(Circle())
                                
                                Button(action: {}) {
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 16))
                                        .foregroundColor(.white)
                                        .frame(width: 32, height: 32)
                                        .background(Color.gray)
                                        .clipShape(Circle())
                                }
                                .offset(x: 8, y: 8)
                            }
                            
                            VStack(spacing: 8) {
                                Text("\(currentUser.name), \(currentUser.age)")
                                    .font(.system(size: 20, weight: .bold))
                                    .foregroundColor(.black)
                                
                                HStack {
                                    Image(systemName: "location.fill")
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                    Text(currentUser.location)
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                }
                                
                                HStack {
                                    Image(systemName: "briefcase.fill")
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                    Text(currentUser.occupation)
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                }
                            }
                        }
                    }
                    
                    // About Me Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("About Me")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                            
                            Text(currentUser.bio)
                                .font(.system(size: 14))
                                .foregroundColor(.gray)
                                .lineSpacing(4)
                        }
                    }
                    
                    // Coffee Preference Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Image(systemName: "cup.and.saucer.fill")
                                    .font(.system(size: 16))
                                    .foregroundColor(.black)
                                Text("Coffee Preference")
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundColor(.black)
                            }
                            
                            Text(currentUser.coffeePreference)
                                .font(.system(size: 14))
                                .foregroundColor(.gray)
                        }
                    }
                    
                    // Interests Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Interests")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                            
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                                ForEach(currentUser.interests, id: \.self) { interest in
                                    Badge(interest, color: .secondary)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                            }
                        }
                    }
                    
                    // Available Times Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Available Times")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                ForEach(currentUser.availableTimes ?? [], id: \.self) { time in
                                    HStack {
                                        Text("•")
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                        Text(time)
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                    }
                                }
                            }
                        }
                    }
                    
                    // Favorite Coffee Spots Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Favorite Coffee Spots")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                ForEach(currentUser.favoriteSpots ?? [], id: \.self) { spot in
                                    HStack {
                                        Text("•")
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                        Text(spot)
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                    }
                                }
                            }
                        }
                    }
                    
                    // Chat Topics Card
                    Card {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Chat Topics")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                            
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                                ForEach(currentUser.chatTopics ?? [], id: \.self) { topic in
                                    Badge(topic, color: .blue)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                            }
                        }
                    }
                    
                    // Edit Profile Button
                    CustomButton("Edit Profile", style: .primary) {
                        showingEditProfile = true
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.horizontal, 16)
            }
        }
        .background(Color.gray.opacity(0.05))
        .sheet(isPresented: $showingEditProfile) {
            // Edit Profile View would go here
            Text("Edit Profile Page")
                .padding()
        }
        .sheet(isPresented: $showingSettings) {
            SettingsPageView()
        }
    }
}

#Preview {
    ProfilePageView()
}
