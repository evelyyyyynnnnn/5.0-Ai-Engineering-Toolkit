//
//  SettingsPageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct SettingsPageView: View {
    @Environment(\.presentationMode) var presentationMode
    
    @State private var notifications = true
    @State private var location = true
    @State private var ageRange: ClosedRange<Double> = 22...35
    @State private var maxDistance: Double = 5
    @State private var coffeePreference = "any"
    @State private var isProfilePaused = false
    @State private var showLastActive = true
    @State private var isVerified = true
    @State private var showingBlockList = false
    @State private var showingCommentFilter = false
    @State private var showingEditEmail = false
    @State private var phoneNumber = "+1 607 262 4282"
    @State private var emailAddress = "evelyn@example.com"
    
    private let coffeePreferences = [
        "any": "Any",
        "espresso": "Espresso",
        "americano": "Americano",
        "latte": "Latte",
        "cappuccino": "Cappuccino",
        "handdrip": "Pour Over",
        "specialty": "Specialty Coffee"
    ]
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Button(action: { presentationMode.wrappedValue.dismiss() }) {
                    Image(systemName: "xmark")
                        .font(.system(size: 18, weight: .medium))
                        .foregroundColor(.black)
                }
                
                Spacer()
                
                Text("Account Settings")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.black)
                
                Spacer()
                
                // Invisible button to center the title
                Button(action: {}) {
                    Image(systemName: "xmark")
                        .font(.system(size: 18, weight: .medium))
                        .foregroundColor(.clear)
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
            .background(Color.white)
            
            ScrollView {
                VStack(spacing: 0) {
                    // Profile Section
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Profile")
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 20)
                            .padding(.top, 24)
                            .padding(.bottom, 8)
                        
                        VStack(spacing: 0) {
                            // Pause Profile
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Pause")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(.black)
                                    Text("Pausing prevents your profile from being shown to new people. You can still chat with your current matches.")
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                        .lineLimit(nil)
                                }
                                
                                Spacer()
                                
                                Toggle("", isOn: $isProfilePaused)
                                    .toggleStyle(SwitchToggleStyle(tint: .black))
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Show Last Active Status
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Show Last Active Status")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(.black)
                                    Text("People viewing your profile can see your last active status, and you can see theirs. Your matches won't be shown your last active status.")
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                        .lineLimit(nil)
                                }
                                
                                Spacer()
                                
                                Toggle("", isOn: $showLastActive)
                                    .toggleStyle(SwitchToggleStyle(tint: .black))
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                        }
                        .background(Color.white)
                    }
                    
                    // Safety Section
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Safety")
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 20)
                            .padding(.top, 24)
                            .padding(.bottom, 8)
                        
                        VStack(spacing: 0) {
                            // Selfie Verification
                            Button(action: {}) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("Selfie Verification")
                                            .font(.system(size: 16, weight: .semibold))
                                            .foregroundColor(.black)
                                        Text("You're verified.")
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                    }
                                    
                                    Spacer()
                                    
                                    HStack(spacing: 8) {
                                        Image(systemName: "checkmark.circle.fill")
                                            .font(.system(size: 16))
                                            .foregroundColor(.black)
                                        
                                        Image(systemName: "chevron.right")
                                            .font(.system(size: 14, weight: .medium))
                                            .foregroundColor(.black)
                                    }
                                }
                                .padding(.horizontal, 20)
                                .padding(.vertical, 16)
                            }
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Block List
                            Button(action: { showingBlockList = true }) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("Block List")
                                            .font(.system(size: 16, weight: .semibold))
                                            .foregroundColor(.black)
                                        Text("Block people you know. They won't see you and you won't see them on BrewMeet.")
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                            .lineLimit(nil)
                                    }
                                    
                                    Spacer()
                                    
                                    Image(systemName: "chevron.right")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.black)
                                }
                                .padding(.horizontal, 20)
                                .padding(.vertical, 16)
                            }
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Comment Filter
                            Button(action: { showingCommentFilter = true }) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("Comment Filter")
                                            .font(.system(size: 16, weight: .semibold))
                                            .foregroundColor(.black)
                                        Text("Hide likes from people who use disrespectful language in their comments.")
                                            .font(.system(size: 14))
                                            .foregroundColor(.gray)
                                            .lineLimit(nil)
                                    }
                                    
                                    Spacer()
                                    
                                    Image(systemName: "chevron.right")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.black)
                                }
                                .padding(.horizontal, 20)
                                .padding(.vertical, 16)
                            }
                        }
                        .background(Color.white)
                    }
                    
                    // Phone & Email Section
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Phone & email")
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 20)
                            .padding(.top, 24)
                            .padding(.bottom, 8)
                        
                        VStack(spacing: 0) {
                            // Phone Number
                            HStack {
                                Text(phoneNumber)
                                    .font(.system(size: 16))
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                Image(systemName: "checkmark")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.black)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Email Address
                            HStack {
                                Text(emailAddress)
                                    .font(.system(size: 16))
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                HStack(spacing: 8) {
                                    Image(systemName: "checkmark")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.black)
                                    
                                    Button("Edit") {
                                        showingEditEmail = true
                                    }
                                    .font(.system(size: 16, weight: .medium))
                                    .foregroundColor(.black)
                                }
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                        }
                        .background(Color.white)
                    }
                    
                    // Discovery Preferences
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Discovery Preferences")
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 20)
                            .padding(.top, 24)
                            .padding(.bottom, 8)
                        
                        VStack(spacing: 0) {
                            // Age Range
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Age Range: \(Int(ageRange.lowerBound)) - \(Int(ageRange.upperBound)) years")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.black)
                                
                                RangeSlider(value: $ageRange, bounds: 18...60, step: 1)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Distance
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Max Distance: \(Int(maxDistance)) km")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.black)
                                
                                Slider(value: $maxDistance, in: 1...50, step: 1)
                                    .accentColor(.black)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                            
                            Divider()
                                .padding(.leading, 20)
                            
                            // Coffee Preference
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Coffee Preference")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.black)
                                
                                Picker("Coffee Preference", selection: $coffeePreference) {
                                    ForEach(Array(coffeePreferences.keys.sorted()), id: \.self) { key in
                                        Text(coffeePreferences[key] ?? key).tag(key)
                                    }
                                }
                                .pickerStyle(MenuPickerStyle())
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(Color.gray.opacity(0.1))
                                .cornerRadius(8)
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                        }
                        .background(Color.white)
                    }
                    
                    // Notifications
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Notifications")
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 20)
                            .padding(.top, 24)
                            .padding(.bottom, 8)
                        
                        VStack(spacing: 0) {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Push Notifications")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(.black)
                                    Text("Receive notifications for new matches and messages")
                                        .font(.system(size: 14))
                                        .foregroundColor(.gray)
                                }
                                
                                Spacer()
                                
                                Toggle("", isOn: $notifications)
                                    .toggleStyle(SwitchToggleStyle(tint: .black))
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 16)
                        }
                        .background(Color.white)
                    }
                    
                    // Account Actions
                    VStack(spacing: 12) {
                        Button(action: {}) {
                            Text("Pause Account")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.black)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 16)
                                .background(Color.white)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.black, lineWidth: 1)
                                )
                                .cornerRadius(8)
                        }
                        
                        Button(action: {}) {
                            Text("Log Out")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.red)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 16)
                                .background(Color.white)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.red, lineWidth: 1)
                                )
                                .cornerRadius(8)
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 24)
                    .padding(.bottom, 40)
                }
            }
        }
        .background(Color.gray.opacity(0.05))
        .sheet(isPresented: $showingBlockList) {
            BlockListView()
        }
        .sheet(isPresented: $showingCommentFilter) {
            CommentFilterView()
        }
        .sheet(isPresented: $showingEditEmail) {
            EditEmailView(email: $emailAddress)
        }
    }
}

struct ToggleRow: View {
    let title: String
    @Binding var isOn: Bool
    
    var body: some View {
        HStack {
            Text(title)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.black)
            
            Spacer()
            
            Toggle("", isOn: $isOn)
                .toggleStyle(SwitchToggleStyle())
        }
    }
}

struct RangeSlider: View {
    @Binding var value: ClosedRange<Double>
    let bounds: ClosedRange<Double>
    let step: Double
    
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // Track
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .frame(height: 4)
                    .cornerRadius(2)
                
                // Active range
                Rectangle()
                    .fill(Color.black)
                    .frame(width: geometry.size.width * (value.upperBound - value.lowerBound) / (bounds.upperBound - bounds.lowerBound))
                    .offset(x: geometry.size.width * (value.lowerBound - bounds.lowerBound) / (bounds.upperBound - bounds.lowerBound))
                    .cornerRadius(2)
                
                // Thumbs
                HStack {
                    Circle()
                        .fill(Color.black)
                        .frame(width: 20, height: 20)
                        .offset(x: geometry.size.width * (value.lowerBound - bounds.lowerBound) / (bounds.upperBound - bounds.lowerBound))
                        .gesture(
                            DragGesture()
                                .onChanged { gesture in
                                    let newValue = bounds.lowerBound + (gesture.location.x / geometry.size.width) * (bounds.upperBound - bounds.lowerBound)
                                    let clampedValue = max(bounds.lowerBound, min(newValue, value.upperBound - step))
                                    value = clampedValue...value.upperBound
                                }
                        )
                    
                    Spacer()
                    
                    Circle()
                        .fill(Color.black)
                        .frame(width: 20, height: 20)
                        .offset(x: -geometry.size.width * (bounds.upperBound - value.upperBound) / (bounds.upperBound - bounds.lowerBound))
                        .gesture(
                            DragGesture()
                                .onChanged { gesture in
                                    let newValue = bounds.lowerBound + (gesture.location.x / geometry.size.width) * (bounds.upperBound - bounds.lowerBound)
                                    let clampedValue = max(value.lowerBound + step, min(newValue, bounds.upperBound))
                                    value = value.lowerBound...clampedValue
                                }
                        )
                }
            }
        }
        .frame(height: 20)
    }
}

// MARK: - Supporting Views

struct BlockListView: View {
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Block List")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding()
                
                Text("No blocked users")
                    .foregroundColor(.gray)
                    .padding()
                
                Spacer()
            }
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                trailing: Button("Done") {
                    presentationMode.wrappedValue.dismiss()
                }
            )
        }
    }
}

struct CommentFilterView: View {
    @Environment(\.presentationMode) var presentationMode
    @State private var isEnabled = true
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Comment Filter")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding()
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("Hide likes from people who use disrespectful language in their comments.")
                        .font(.body)
                        .foregroundColor(.gray)
                    
                    HStack {
                        Text("Enable Comment Filter")
                            .font(.headline)
                        
                        Spacer()
                        
                        Toggle("", isOn: $isEnabled)
                            .toggleStyle(SwitchToggleStyle(tint: .black))
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                }
                .padding()
                
                Spacer()
            }
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                trailing: Button("Done") {
                    presentationMode.wrappedValue.dismiss()
                }
            )
        }
    }
}

struct EditEmailView: View {
    @Environment(\.presentationMode) var presentationMode
    @Binding var email: String
    @State private var newEmail: String = ""
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Edit Email")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding()
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("Email Address")
                        .font(.headline)
                    
                    TextField("Enter email address", text: $newEmail)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }
                .padding()
                
                Spacer()
            }
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("Cancel") {
                    presentationMode.wrappedValue.dismiss()
                },
                trailing: Button("Save") {
                    email = newEmail
                    presentationMode.wrappedValue.dismiss()
                }
            )
            .onAppear {
                newEmail = email
            }
        }
    }
}

#Preview {
    SettingsPageView()
}
