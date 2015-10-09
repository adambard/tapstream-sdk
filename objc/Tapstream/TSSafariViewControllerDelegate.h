//
//  TSSafariViewControllerDelegate.h
//  ExampleApp
//
//  Created by Adam Bard on 2015-09-12.
//  Copyright © 2015 Example. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TSHelpers.h"

#if (TEST_IOS || TARGET_OS_IPHONE || TARGET_IPHONE_SIMULATOR)
#import <UIKit/UIKit.h>
#endif

@interface TSSafariViewControllerDelegate : UIViewController

@property(nonatomic, STRONG_OR_RETAIN) NSURL* url;
@property(nonatomic, copy) void (^completion)(void);
@property(nonatomic, STRONG_OR_RETAIN) UIWindow* hiddenWindow;

+ (void)presentSafariViewControllerWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion;
@end